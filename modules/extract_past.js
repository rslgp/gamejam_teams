const axios = require('axios');
const cheerio = require('cheerio');

const URL = 'https://itch.io/jams/past';

async function fetchJams() {
    try {
        const { data } = await axios.get(URL);
        const $ = cheerio.load(data);
        const jamUrls = new Set();
        
        $('h3 > a').each((_, element) => {
            const jamUrl = $(element).attr('href');
            if (jamUrl.startsWith('/jam/')) {
                jamUrls.add(`https://itch.io${jamUrl}`);
            }
        });
        
        console.log([...jamUrls]);
    } catch (error) {
        console.error('Error fetching jams:', error);
    }
}

fetchJams();
