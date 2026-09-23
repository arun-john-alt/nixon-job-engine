// Authentic employer marks bundled locally; no remote image requests.
const logos = {
  'Tactive Software Systems':'tactive', 'Nokia':'nokia', 'YipitData':'yipitdata', 'Made Card':'madecard', 'AHL – Saaf AI':'saaf', 'WPP':'wpp', 'Xerago':'xerago', 'Novature Tech':'novature',
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
 'Tactive Software Systems':['https://www.tactivesoft.com/company-overview/','Develops construction ERP software under its own Tactive brand.'],
 'Nokia':['https://www.nokia.com/','Develops networking equipment and software.'],
 'YipitData':['https://www.yipitdata.com/careers-teams/product--engineering','Develops market intelligence data products.'],
 'Made Card':['https://www.madecard.com/about','Develops a homeowner credit-card and home-management platform.'],
 'AHL – Saaf AI':['https://jobs.ashbyhq.com/ahl-saafai/ea0fdc4d-336e-46df-9ed6-10539f6ff2e5','Employer describes its own AI-powered mortgage platform.'],
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
