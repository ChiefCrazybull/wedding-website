"""Country name -> ISO 3166-1 alpha-2 -> flag emoji.

Used only to pre-fill the flag field when adding a new country, so the table
does not have to be exhaustive or authoritative - anything it misses just means
typing the emoji by hand.  Keys are matched case- and punctuation-insensitively
(see `normalise`), and a few common alternate names are included.
"""

import unicodedata

CODES = {
    "afghanistan": "AF", "albania": "AL", "algeria": "DZ", "andorra": "AD",
    "angola": "AO", "antigua and barbuda": "AG", "argentina": "AR",
    "armenia": "AM", "aruba": "AW", "australia": "AU", "austria": "AT",
    "azerbaijan": "AZ", "bahamas": "BS", "bahrain": "BH", "bangladesh": "BD",
    "barbados": "BB", "belarus": "BY", "belgium": "BE", "belize": "BZ",
    "benin": "BJ", "bermuda": "BM", "bhutan": "BT", "bolivia": "BO",
    "bosnia and herzegovina": "BA", "botswana": "BW", "brazil": "BR",
    "brunei": "BN", "bulgaria": "BG", "burkina faso": "BF", "burundi": "BI",
    "cambodia": "KH", "cameroon": "CM", "canada": "CA", "cape verde": "CV",
    "cayman islands": "KY", "central african republic": "CF", "chad": "TD",
    "chile": "CL", "china": "CN", "colombia": "CO", "comoros": "KM",
    "congo": "CG", "cook islands": "CK", "costa rica": "CR",
    "cote divoire": "CI", "croatia": "HR", "cuba": "CU", "curacao": "CW",
    "cyprus": "CY", "czechia": "CZ", "czech republic": "CZ",
    "democratic republic of the congo": "CD", "denmark": "DK",
    "djibouti": "DJ", "dominica": "DM", "dominican republic": "DO",
    "ecuador": "EC", "egypt": "EG", "el salvador": "SV",
    "equatorial guinea": "GQ", "eritrea": "ER", "estonia": "EE",
    "eswatini": "SZ", "ethiopia": "ET", "fiji": "FJ", "finland": "FI",
    "france": "FR", "french polynesia": "PF", "gabon": "GA", "gambia": "GM",
    "georgia": "GE", "germany": "DE", "ghana": "GH", "gibraltar": "GI",
    "greece": "GR", "greenland": "GL", "grenada": "GD", "guadeloupe": "GP",
    "guam": "GU", "guatemala": "GT", "guinea": "GN", "guinea bissau": "GW",
    "guyana": "GY", "haiti": "HT", "honduras": "HN", "hong kong": "HK",
    "hungary": "HU", "iceland": "IS", "india": "IN", "indonesia": "ID",
    "iran": "IR", "iraq": "IQ", "ireland": "IE", "israel": "IL",
    "italy": "IT", "ivory coast": "CI", "jamaica": "JM", "japan": "JP",
    "jordan": "JO", "kazakhstan": "KZ", "kenya": "KE", "kiribati": "KI",
    "kosovo": "XK", "kuwait": "KW", "kyrgyzstan": "KG", "laos": "LA",
    "latvia": "LV", "lebanon": "LB", "lesotho": "LS", "liberia": "LR",
    "libya": "LY", "liechtenstein": "LI", "lithuania": "LT",
    "luxembourg": "LU", "macao": "MO", "macau": "MO", "madagascar": "MG",
    "malawi": "MW", "malaysia": "MY", "maldives": "MV", "mali": "ML",
    "malta": "MT", "marshall islands": "MH", "martinique": "MQ",
    "mauritania": "MR", "mauritius": "MU", "mexico": "MX", "micronesia": "FM",
    "moldova": "MD", "monaco": "MC", "mongolia": "MN", "montenegro": "ME",
    "montserrat": "MS", "morocco": "MA", "mozambique": "MZ", "myanmar": "MM",
    "namibia": "NA", "nauru": "NR", "nepal": "NP", "netherlands": "NL",
    "new caledonia": "NC", "new zealand": "NZ", "nicaragua": "NI",
    "niger": "NE", "nigeria": "NG", "north korea": "KP",
    "north macedonia": "MK", "macedonia": "MK", "norway": "NO", "oman": "OM",
    "pakistan": "PK", "palau": "PW", "palestine": "PS", "panama": "PA",
    "papua new guinea": "PG", "paraguay": "PY", "peru": "PE",
    "philippines": "PH", "poland": "PL", "portugal": "PT",
    "puerto rico": "PR", "qatar": "QA", "reunion": "RE", "romania": "RO",
    "russia": "RU", "rwanda": "RW", "saint kitts and nevis": "KN",
    "saint lucia": "LC", "saint vincent and the grenadines": "VC",
    "samoa": "WS", "san marino": "SM", "sao tome and principe": "ST",
    "saudi arabia": "SA", "senegal": "SN", "serbia": "RS",
    "seychelles": "SC", "sierra leone": "SL", "singapore": "SG",
    "sint maarten": "SX", "slovakia": "SK", "slovenia": "SI",
    "solomon islands": "SB", "somalia": "SO", "south africa": "ZA",
    "south korea": "KR", "korea": "KR", "south sudan": "SS", "spain": "ES",
    "sri lanka": "LK", "sudan": "SD", "suriname": "SR", "sweden": "SE",
    "switzerland": "CH", "syria": "SY", "taiwan": "TW", "tajikistan": "TJ",
    "tanzania": "TZ", "thailand": "TH", "timor leste": "TL", "togo": "TG",
    "tonga": "TO", "trinidad and tobago": "TT", "tunisia": "TN",
    "turkey": "TR", "turkiye": "TR", "turkmenistan": "TM",
    "turks and caicos islands": "TC", "tuvalu": "TV", "uganda": "UG",
    "ukraine": "UA", "united arab emirates": "AE", "united kingdom": "GB",
    "great britain": "GB", "england": "GB", "scotland": "GB",
    "united states": "US", "united states of america": "US", "usa": "US",
    "uruguay": "UY", "us virgin islands": "VI", "uzbekistan": "UZ",
    "vanuatu": "VU", "vatican city": "VA", "venezuela": "VE",
    "vietnam": "VN", "yemen": "YE", "zambia": "ZM", "zimbabwe": "ZW",
}

# Spanish names, so the Spanish field can fill the flag in too.
CODES_ES = {
    "alemania": "DE", "arabia saudita": "SA", "belgica": "BE",
    "bosnia y herzegovina": "BA", "brasil": "BR", "canada": "CA",
    "ciudad del vaticano": "VA", "corea del sur": "KR", "croacia": "HR",
    "dinamarca": "DK", "egipto": "EG", "emiratos arabes unidos": "AE",
    "escocia": "GB", "eslovaquia": "SK", "eslovenia": "SI", "espana": "ES",
    "estados unidos": "US", "filipinas": "PH", "finlandia": "FI",
    "francia": "FR", "grecia": "GR", "hungria": "HU", "inglaterra": "GB",
    "irlanda": "IE", "islandia": "IS", "italia": "IT", "japon": "JP",
    "letonia": "LV", "lituania": "LT", "macedonia del norte": "MK",
    "marruecos": "MA", "mexico": "MX", "noruega": "NO",
    "nueva zelanda": "NZ", "paises bajos": "NL", "peru": "PE",
    "polonia": "PL", "reino unido": "GB", "republica checa": "CZ",
    "republica dominicana": "DO", "rumania": "RO", "rusia": "RU",
    "suecia": "SE", "suiza": "CH", "turquia": "TR",
}


def normalise(name):
    """Fold a display name down to a lookup key: no accents, letters and spaces."""
    text = unicodedata.normalize("NFKD", name or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("&amp;", " and ").replace("&", " and ")
    text = "".join(c if c.isalnum() else " " for c in text.lower())
    return " ".join(text.split())


def code_to_emoji(code):
    """'PE' -> the regional-indicator pair that renders as a flag."""
    code = (code or "").strip().upper()
    if len(code) != 2 or not code.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code)


def emoji_for(name):
    """Best-guess flag emoji for a country name, or "" if it isn't known."""
    key = normalise(name)
    code = CODES.get(key) or CODES_ES.get(key)
    return code_to_emoji(code) if code else ""


def lookup_table():
    """{normalised name: emoji} for the browser to auto-fill from."""
    table = {}
    for src in (CODES, CODES_ES):
        for key, code in src.items():
            emoji = code_to_emoji(code)
            if emoji:
                table[key] = emoji
    return table
