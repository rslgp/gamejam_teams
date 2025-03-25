const axios = require('axios');
const cheerio = require('cheerio');
const { extractTeamInfo } = require('./extract_team');

const SELECTOR = {
    profile_bio: 'div.user_profile.formatted',
    game_description: 'div.formatted_description.user_formatted',
    game_authors: '.game_info_panel_widget > table > tbody > tr:nth-child(7) > td:nth-child(2)'
}
//'div.user_profile.formatted'
//'div.formatted_description user_formatted'
const extract_data = async (URL, selectors) => {
    const { data } = await axios.get(URL);
    const $ = cheerio.load(data);
    const content_text = [];
    for (const selector of selectors)
        $(selector).each((index, elem) => content_text.push($(elem).text()))
    const result = content_text.join("\n");
    //console.log(result);

    return result;
}
// extract_data('https://bippinbits.itch.io/', [SELECTOR.profile_bio]);
// extract_data('https://zephyo.itch.io/stop-burying-me-alive-beautiful', [SELECTOR.game_description]);
let total=[];
async function run(){
    for(let url of ['https://bippinbits.itch.io/squeezlings','https://pulni.itch.io/sneakerdoodle', 'https://aquanoctis.itch.io/onedaybetter', 'https://golen.itch.io/fire-and-dice', 'https://riuku.itch.io/randomancer'])
        {
            total.push(url + extractTeamInfo(await extract_data(url,[SELECTOR.game_description])) );
        
        }
        console.log(total.join('\n'));
        
}
run();
const getAuthors = (URL) => {
    document.querySelector("").textContent

}