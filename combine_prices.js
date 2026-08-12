const fs = require('fs');

// Load Bot 1 prices
const bot1Map = JSON.parse(fs.readFileSync('C:\\Users\\anes2\\.gemini\\antigravity\\scratch\\lzt_telegram_monitor\\sell_prices.json', 'utf-8'));

const bot2Raw = `
🇩🇿 Algeria (+213) 🇩🇿 | Free: 0.4$
🇦🇸 American Samoa (+1) 🇦🇸 | Free: 0.35$
🇦🇴 Angola (+244) 🇦🇴 | Free: 0.15$
🇦🇺 Australia (+61) 🇦🇺 | Free: 1.4$
🇦🇹 Austria (+43) 🇦🇹 | Free: 0.8$
🇦🇿 Azerbaijan (+994) 🇦🇿 | Free: 1.15$
🇧🇭 Bahrain (+973) 🇧🇭 | Free: 1.5$
🇧🇩 Bangladesh (+880) 🇧🇩 | Free: 0.15$
🇧🇾 Belarus (+375) 🇧🇾 | Free: 1.6$
🇧🇪 Belgium (+32) 🇧🇪 | Free: 1.15$
🇧🇿 Belize (+501) 🇧🇿 | Free: 0.35$
🇧🇯 Benin (+229) 🇧🇯 | Free: 0.13$
🇧🇴 Bolivia (+591) 🇧🇴 | Free: 1.15$
🇧🇳 Brunei Darussalam (+673) 🇧🇳 | Free: 0.35$
🇧🇬 Bulgaria (+359) 🇧🇬 | Free: 0.85$
🇧🇫 Burkina Faso (+226) 🇧🇫 | Free: 0.35$
🇧🇮 Burundi (+257) 🇧🇮 | Free: 0.35$
🇨🇻 Cabo Verde (+238) 🇨🇻 | Free: 0.3$
🇰🇲 Comoros (+269) 🇰🇲 | Free: 0.65$
🇨🇰 Cook Islands (+682) 🇨🇰 | Free: 0.35$
🇨🇷 Costa Rica (+506) 🇨🇷 | Free: 0.5$
🇭🇷 Croatia (+385) 🇭🇷 | Free: 1.0$
🇨🇮 Côte d'Ivoire (+225) 🇨🇮 | Free: 0.7$
🇩🇰 Denmark (+45) 🇩🇰 | Free: 1.3$
🇩🇯 Djibouti (+253) 🇩🇯 | Free: 0.4$
🇩🇴 Dominican Republic (+1) 🇩🇴 | Free: 0.6$
🇪🇨 Ecuador (+593) 🇪🇨 | Free: 0.55$
🇸🇻 El Salvador (+503) 🇸🇻 | Free: 0.6$
🇪🇷 Eritrea (+291) 🇪🇷 | Free: 0.55$
🇫🇰 Falkland Islands (Malvinas) (+500) 🇫🇰 | Free: 0.5$
🇫🇯 Fiji (+679) 🇫🇯 | Free: 0.6$
🇫🇮 Finland (+358) 🇫🇮 | Free: 0.75$
🇫🇷 France (+33) 🇫🇷 | Free: 0.75$
🇬🇦 Gabon (+241) 🇬🇦 | Free: 0.35$
🇬🇲 Gambia (+220) 🇬🇲 | Free: 0.35$
🇩🇪 Germany (+49) 🇩🇪 | Free: 0.95$
🇬🇭 Ghana (+233) 🇬🇭 | Free: 0.35$
🇬🇱 Greenland (+299) 🇬🇱 | Free: 0.45$
🇬🇹 Guatemala (+502) 🇬🇹 | Free: 0.45$
🇭🇹 Haiti (+509) 🇭🇹 | Free: 0.5$
🇭🇺 Hungary (+36) 🇭🇺 | Free: 0.65$
🇮🇸 Iceland (+354) 🇮🇸 | Free: 0.7$
🇮🇹 Italy (+39) 🇮🇹 | Free: 0.85$
🇯🇴 Jordan (+962) 🇯🇴 | Free: 0.5$
🇰🇪 Kenya (+254) 🇰🇪 | Free: 0.25$
🇰🇮 Kiribati (+686) 🇰🇮 | Free: 0.4$
🇰🇵 North Korea (+850) 🇰🇵 | Free: 0.2$
🇰🇷 South Korea (+82) 🇰🇷 | Free: 2.1$
🇽🇰 Kosovo (+383) 🇽🇰 | Free: 0.6$
🇰🇬 Kyrgyzstan (+996) 🇰🇬 | Free: 0.7$
🇱🇦 Laos (+856) 🇱🇦 | Free: 0.7$
🇱🇻 Latvia (+371) 🇱🇻 | Free: 1.0$
🇱🇸 Lesotho (+266) 🇱🇸 | Free: 0.3$
🇱🇹 Lithuania (+370) 🇱🇹 | Free: 0.9$
🇱🇺 Luxembourg (+352) 🇱🇺 | Free: 0.85$
🇲🇴 Macao (+853) 🇲🇴 | Free: 1.1$
🇲🇼 Malawi (+265) 🇲🇼 | Free: 0.35$
🇲🇾 Malaysia (+60) 🇲🇾 | Free: 0.4$
🇲🇻 Maldives (+960) 🇲🇻 | Free: 0.5$
🇲🇱 Mali (+223) 🇲🇱 | Free: 0.35$
🇲🇹 Malta (+356) 🇲🇹 | Free: 1.15$
🇲🇶 Martinique (+596) 🇲🇶 | Free: 0.5$
🇲🇩 Moldova (+373) 🇲🇩 | Free: 1.0$
🇲🇨 Monaco (+377) 🇲🇨 | Free: 1.0$
🇲🇦 Morocco (+212) 🇲🇦 | Free: 0.25$
🇲🇿 Mozambique (+258) 🇲🇿 | Free: 0.5$
🇲🇲 Myanmar (+95) 🇲🇲 | Free: 0.15$
🇳🇦 Namibia (+264) 🇳🇦 | Free: 0.4$
🇳🇷 Nauru (+674) 🇳🇷 | Free: 0.35$
🇳🇵 Nepal (+977) 🇳🇵 | Free: 0.35$
🇳🇱 Netherlands (+31) 🇳🇱 | Free: 0.85$
🇳🇨 New Caledonia (+687) 🇳🇨 | Free: 0.35$
🇳🇿 New Zealand (+64) 🇳🇿 | Free: 1.2$
🇳🇮 Nicaragua (+505) 🇳🇮 | Free: 0.45$
🇳🇪 Niger (+227) 🇳🇪 | Free: 0.35$
🇳🇬 Nigeria (+234) 🇳🇬 | Free: 0.2$
🇳🇺 Niue (+683) 🇳🇺 | Free: 0.35$
🇳🇫 Norfolk Island (+672) 🇳🇫 | Free: 0.35$
🇲🇰 North Macedonia (+389) 🇲🇰 | Free: 0.7$
🇳🇴 Norway (+47) 🇳🇴 | Free: 1.1$
🇴🇲 Oman (+968) 🇴🇲 | Free: 0.9$
🇵🇼 Palau (+680) 🇵🇼 | Free: 0.35$
🇵🇸 Palestine, State of (+970) 🇵🇸 | Free: 0.55$
🇵🇦 Panama (+507) 🇵🇦 | Free: 0.8$
🇵🇾 Paraguay (+595) 🇵🇾 | Free: 0.45$
🇵🇱 Poland (+48) 🇵🇱 | Free: 0.4$
🇵🇹 Portugal (+351) 🇵🇹 | Free: 0.55$
🇵🇷 Puerto Rico (+1) 🇵🇷 | Free: 0.4$
🇶🇦 Qatar (+974) 🇶🇦 | Free: 1.3$
🇷🇼 Rwanda (+250) 🇷🇼 | Free: 0.3$
🇻🇨 Saint Vincent and the Grenadines (+1) 🇻🇨 | Free: 0.35$
🇼🇸 Samoa (+685) 🇼🇸 | Free: 0.35$
🇸🇲 San Marino (+378) 🇸🇲 | Free: 0.9$
🇸🇹 Sao Tome and Principe (+239) 🇸🇹 | Free: 0.4$
🇸🇦 Saudi Arabia (+966) 🇸🇦 | Free: 0.4$
🇸🇳 Senegal (+221) 🇸🇳 | Free: 0.5$
🇷🇸 Serbia (+381) 🇷🇸 | Free: 0.9$
🇸🇱 Sierra Leone (+232) 🇸🇱 | Free: 0.2$
🇸🇬 Singapore (+65) 🇸🇬 | Free: 1.25$
🇸🇰 Slovakia (+421) 🇸🇰 | Free: 1.1$
🇸🇮 Slovenia (+386) 🇸🇮 | Free: 1.3$
🇸🇧 Solomon Islands (+677) 🇸🇧 | Free: 0.35$
🇿🇦 South Africa (+27) 🇿🇦 | Free: 0.15$
🇱🇰 Sri Lanka (+94) 🇱🇰 | Free: 0.55$
🇸🇩 Sudan (+249) 🇸🇩 | Free: 0.45$
🇸🇪 Sweden (+46) 🇸🇪 | Free: 0.7$
🇨🇭 Switzerland (+41) 🇨🇭 | Free: 1.5$
🇹🇼 Taiwan (+886) 🇹🇼 | Free: 1.4$
🇹🇬 Togo (+228) 🇹🇬 | Free: 0.25$
🇹🇰 Tokelau (+690) 🇹🇰 | Free: 0.2$
🇹🇴 Tonga (+676) 🇹🇴 | Free: 0.4$
🇹🇹 Trinidad and Tobago (+1) 🇹🇹 | Free: 0.5$
🇹🇳 Tunisia (+216) 🇹🇳 | Free: 0.5$
🇹🇲 Turkmenistan (+993) 🇹🇲 | Free: 0.55$
🇹🇻 Tuvalu (+688) 🇹🇻 | Free: 0.35$
🇹🇷 Türkiye (+90) 🇹🇷 | Free: 0.5$
🇺🇦 Ukraine (+380) 🇺🇦 | Free: 1.6$
🇦🇪 United Arab Emirates (+971) 🇦🇪 | Free: 1.65$
🇺🇾 Uruguay (+598) 🇺🇾 | Free: 0.6$
🇺🇿 Uzbekistan (+998) 🇺🇿 | Free: 0.4$
🇻🇺 Vanuatu (+678) 🇻🇺 | Free: 0.4$
🇼🇫 Wallis and Futuna (+681) 🇼🇫 | Free: 0.35$
🇾🇪 Yemen (+967) 🇾🇪 | Free: 0.4$
🇿🇲 Zambia (+260) 🇿🇲 | Free: 0.4$
🇿🇼 Zimbabwe (+263) 🇿🇼 | Free: 0.2$
`;

// Extract country mapping from phone codes or country names for Bot 2
// Phone code mapping
const phoneToCode = {
  "213": "DZ", "1": "US", "244": "AO", "61": "AU", "43": "AT", "994": "AZ", "973": "BH",
  "880": "BD", "375": "BY", "32": "BE", "501": "BZ", "229": "BJ", "591": "BO", "673": "BN",
  "359": "BG", "226": "BF", "257": "BI", "238": "CV", "269": "KM", "682": "CK", "506": "CR",
  "385": "HR", "225": "CI", "45": "DK", "253": "DJ", "593": "EC", "503": "SV", "291": "ER",
  "500": "FK", "679": "FJ", "358": "FI", "33": "FR", "241": "GA", "220": "GM", "49": "DE",
  "233": "GH", "299": "GL", "502": "GT", "509": "HT", "36": "HU", "354": "IS", "39": "IT",
  "962": "JO", "254": "KE", "686": "KI", "850": "KP", "82": "KR", "383": "XK", "996": "KG",
  "856": "LA", "371": "LV", "266": "LS", "370": "LT", "352": "LU", "853": "MO", "265": "MW",
  "60": "MY", "960": "MV", "223": "ML", "356": "MT", "596": "MQ", "373": "MD", "377": "MC",
  "212": "MA", "258": "MZ", "95": "MM", "264": "NA", "674": "NR", "977": "NP", "31": "NL",
  "687": "NC", "64": "NZ", "505": "NI", "227": "NE", "234": "NG", "683": "NU", "672": "NF",
  "389": "MK", "47": "NO", "968": "OM", "680": "PW", "970": "PS", "507": "PA", "595": "PY",
  "48": "PL", "351": "PT", "974": "QA", "250": "RW", "685": "WS", "378": "SM", "239": "ST",
  "966": "SA", "221": "SN", "381": "RS", "232": "SL", "65": "SG", "421": "SK", "386": "SI",
  "677": "SB", "27": "ZA", "94": "LK", "249": "SD", "46": "SE", "41": "CH", "886": "TW",
  "228": "TG", "690": "TK", "676": "TO", "216": "TN", "993": "TM", "688": "TV", "90": "TR",
  "380": "UA", "971": "AE", "598": "UY", "998": "UZ", "678": "VU", "681": "WF", "967": "YE",
  "260": "ZM", "263": "ZW"
};

const bot2Map = {};

bot2Raw.split('\n').forEach(line => {
  const m = line.match(/\(\+(\d+)\).*?:\s*([0-9.]+)[\$]/);
  if (m) {
    const phoneCode = m[1];
    const priceUSD = parseFloat(m[2]);
    const ccode = phoneToCode[phoneCode];
    if (ccode) {
      bot2Map[ccode] = priceUSD;
    }
  }
});

// Combine Bot 1 and Bot 2 into unified structure
const combinedMap = {};
const allKeys = new Set([...Object.keys(bot1Map), ...Object.keys(bot2Map)]);

allKeys.forEach(code => {
  const p1 = bot1Map[code] || 0;
  const p2 = bot2Map[code] || 0;
  
  let bestPrice = p1;
  let bestBot = "Bot 1";
  
  if (p2 > p1) {
    bestPrice = p2;
    bestBot = "Bot 2";
  }
  
  combinedMap[code] = {
    best_usd: bestPrice,
    best_bot: bestBot,
    bot1_usd: p1,
    bot2_usd: p2
  };
});

console.log(`Processed ${allKeys.size} countries from Bot 1 & Bot 2 combined.`);

fs.writeFileSync(
  'C:\\Users\\anes2\\.gemini\\antigravity\\scratch\\lzt_telegram_monitor\\sell_prices.json',
  JSON.stringify(combinedMap, null, 2)
);

console.log("Updated sell_prices.json with combined Bot 1 and Bot 2 prices!");
