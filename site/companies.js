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
  "UST": "ust", "Amazon":"amazon", "Jitterbit":"jitterbit", "Hydsoft":"hydsoft", "Ingram Micro":"ingram", "NETGEAR":"netgear"
};
export function companyLogo(company){const key=Object.hasOwn(logos,company)?logos[company]:null;return key?`assets/companies/${key}.${key==='ust'?'svg':'png'}`:"assets/companies/company.svg";}

// Classification is about the hiring company, not an unnamed client or a pay promise.
const products = {
 'Extreme Networks':['https://www.extremenetworks.com','Develops networking hardware and cloud networking software.'],
 'Logitech':['https://www.logitech.com','Develops branded peripherals and collaboration devices.'],
 'Viasat':['https://www.viasat.com','Develops satellite connectivity systems and related products.'],
 'KLA':['https://www.kla.com','Develops semiconductor and electronics inspection systems.'],
 'Omnissa':['https://www.omnissa.com','Develops digital workspace and endpoint software.'],
 'Arista Networks':['https://www.arista.com','Develops network switches, EOS and cloud networking products.'],
 'Amazon':['https://www.amazon.jobs/content/en/teams/devices-and-services','Develops consumer devices and software services.'],
 'Jitterbit':['https://www.jitterbit.com','Develops the Harmony integration and automation platform.'],
 'NETGEAR':['https://www.netgear.com','Develops branded networking devices and management software.']
};
export function productCompany(company){return Object.hasOwn(products,company)?{url:products[company][0],basis:products[company][1]}:null;}
