// Authentic employer marks bundled locally; no remote image requests.
const logos = {
  "HCLTech": "hcltech",
  "Virtusa": "virtusa",
  "EPAM Systems": "epam",
  "Extreme Networks": "extreme",
  "Logitech": "logitech",
  "Viasat": "viasat",
  "KLA": "kla",
  "Omnissa": "omnissa",
  "Kumaran Systems": "kumaran",
  "Arista Networks": "arista",
  "Miratech": "miratech",
  "UST": "ust"
};
export function companyLogo(company){const key=Object.hasOwn(logos,company)?logos[company]:null;return key?`assets/companies/${key}.${key==='ust'?'svg':'png'}`:"assets/companies/company.svg";}
