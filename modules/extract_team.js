require('dotenv').config()

function extractGameJamTeam(bioTextunformatted) {
    const bioText = unformatted.toLowerCase();
    const teamHeaders = [
        'team', 'made by', 'credits'
    ];
    
    let teamStartIndex = teamHeaders.map(header => bioText.indexOf(header)).find(index => index !== -1);
    console.log(teamStartIndex);
    if (teamStartIndex === undefined) return extractTeamMembersByPattern(bioText);
    
    const teamSection = bioText.slice(teamStartIndex + teamHeaders.find(header => bioText.includes(header)).length);
    
    const nextSectionMarkers = ['\n\n', '------------', '***', '---', 'download', 'soundtrack', 'fonts:', 'features:', 'known bugs:', 'controls'];
    const teamEndIndex = Math.min(...nextSectionMarkers.map(marker => {
        const idx = teamSection.indexOf(marker);
        return idx !== -1 ? idx : teamSection.length;
    }));
    
    const extractedTeam = teamSection.slice(0, teamEndIndex).trim();
    return extractedTeam ? parseTeamMembers(extractedTeam) : extractTeamMembersByPattern(bioText);
}

function extractTeamMembersByPattern(fullText) {
    const teamMemberRegex = /(^|\n)\s*([a-zà-öø-ÿ][a-zà-öø-ÿ'-]+(?:\s+[a-zà-öø-ÿ][a-zà-öø-ÿ'-]+)*)\s*[-–—:@]*\s*([^\n]+)/gi;
    return [...fullText.matchAll(teamMemberRegex)].map(match => ({
        name: match[2].trim(),
        roles: match[3].trim()
    }));
}

function parseTeamMembers(teamSection) {
    return teamSection.split('\n').map(line => line.trim()).filter(line => line && !/^[-=*]+$/.test(line)).reduce((teamMembers, line) => {
        if (/https?:\/\//i.test(line) && teamMembers.length && !teamMembers.at(-1).roles) {
            teamMembers.at(-1).url = line;
        } else {
            const parts = line.split(/[-–—:@]+|(?: - )|(?: – )|(?: — )/).map(part => part.trim()).filter(Boolean);
            if (parts.length >= 2) {
                teamMembers.push({ name: parts[0], roles: parts.slice(1).join(', ') });
            } else {
                if(parts[0]){
                    const lastCommaIndex = parts[0].lastIndexOf(',');
                    
                    if (lastCommaIndex !== -1) {
                        teamMembers.push({
                            name: parts[0].slice(0, lastCommaIndex).trim(),
                            roles: parts[0].slice(lastCommaIndex + 1).trim()
                        });
                    } else {
                        teamMembers.push({ name: parts[0], roles: '' });
                    }

                }
            }
        }
        return teamMembers;
    }, []);
}


const HF_API_TOKEN = process.env.HUGGING_TOKEN;

const axios = require('axios');

const MODEL = 'mistralai/Mistral-7B-Instruct-v0.3';

async function query(prompt) {
  try {
    const response = await axios.post(
      `https://api-inference.huggingface.co/models/${MODEL}`,
      {
        inputs: prompt,
        parameters: {
          return_full_text: false,
          max_new_tokens: 500,
          temperature: 0.3  // Lower temperature for more factual extraction
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${HF_API_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data[0].generated_text;
  } catch (error) {
    console.error('Error calling Hugging Face API:', error.response?.data || error.message);
    throw error;
  }
}

async function extractTeamInfo(gameBio) {
  const prompt = `<|system|>
You are an information extraction assistant that analyzes game development team bios and extracts structured data.
Always respond with valid JSON format.
</s>
<|user|>
Extract the team information from this game bio and format it as single JSON with:
- roles (object with role names as keys and array of names as values)

Here's the bio:
${gameBio}
</s>
<|assistant|>
`;

  try {
    const response = await query(prompt);
    console.log(response);
    // Extract JSON from the response
    const jsonStart = response.indexOf('{');
    const jsonEnd = response.lastIndexOf('}') + 1;
    const jsonString = response.slice(jsonStart, jsonEnd);
    
    const teamInfo = JSON.parse(jsonString);
    console.log('Extracted Team Information:');
    console.log(JSON.stringify(teamInfo, null, 2));
    
    return teamInfo;
  } catch (error) {
    console.error('Error processing response:', error);
    throw error;
  }
}

// Example usage:
const bioText = `your little squeezlings need help!
though cute and very diligent these tiny creatures always require a little "nudge" in the right direction.
guide their rapid evolution™ and satisfy your hunger!

------------

team:

rené habermann - direction, game design, production, coding
anne hecker - art
raffaele picca - art, coding, game design
luca martinelli - coding, game design
ste - coding
shux - cover art
ron kaiser - coding
martin kvale - sound design
cameron paxton - composing, music production, logo

------------
download the ost here!`;

// console.log(extractGameJamTeam(bioText));

// Run the extraction
extractTeamInfo(bioText);

module.exports = {
    extractTeamInfo
}