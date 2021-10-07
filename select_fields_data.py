import requests
from bs4 import BeautifulSoup
import enum, pycountry, phonenumbers


class Gender(enum.Enum):
    """Gender Enum"""
    Gender = 'Choose Your Gender'
    Male = '♂ Male'
    Female = '♀ Female'

    def __str__(self):
        return self.value


def genders():
    """Creates a list with all the genders for SelectField Choices"""
    gender = [(str(y), y) for y in (Gender)]
    return gender


def countries():
    """Creates a list with all the countries for SelectField Choices"""
    countries = [(None, 'Choose Your Country')]
    choices = [(country.name, all_flags(code=str(country.alpha_2).upper()) + " " + country.name) for country in
               pycountry.countries]
    countries.extend(choices)
    return countries


def all_services():
    """Creates a list with all business services"""
    url = "https://www.indeed.com/career-advice/career-development/business-services-types"
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'lxml')
    service_tags = soup.find_all(name='h3')
    services = []
    for service_tag in service_tags:
        services.append((((str(service_tag.text)[3:]).strip()).title(), ((str(service_tag.text)[3:]).strip()).title()))
    print(services[:30])
    return services[:30]


# I used the method already just for performance
all_services_list = [("Choose Your Company's Service", "Choose Your Company's Service"),
                     ('Software Services', 'Software Services'), ('Training Services', 'Training Services'),
                     ('Event Planning Services', 'Event Planning Services'),
                     ('Ecommerce Services', 'Ecommerce Services'), ('Consulting Services', 'Consulting Services'),
                     ('Marketing Services', 'Marketing Services'),
                     ('Waste Management Services', 'Waste Management Services'),
                     ('Construction Services', 'Construction Services'), ('Legal Services', 'Legal Services'),
                     ('Health And Wellness Services', 'Health And Wellness Services'),
                     ('Insurance Services', 'Insurance Services'), ('Security Services', 'Security Services'),
                     ('Travel Services', 'Travel Services'), ('Research Services', 'Research Services'),
                     ('Design Services', 'Design Services'), ('Finance Services', 'Finance Services'),
                     ('Delivery Services', 'Delivery Services'), ('Real Estate Services', 'Real Estate Services'),
                     ('Child Care Services', 'Child Care Services'), ('Utilities', 'Utilities'),
                     ('Printing Services', 'Printing Services'), ('Personal Services', 'Personal Services'),
                     ('Landscaping', 'Landscaping'), ('Pest Extermination Services', 'Pest Extermination Services'),
                     ('Maintenance Services', 'Maintenance Services'),
                     ('Tech Support Services', 'Tech Support Services'),
                     ('Bookkeeping Services', 'Bookkeeping Services'),
                     ('Video And Photography Services', 'Video And Photography Services'),
                     ('Translation Services', 'Translation Services'), ('Parking Services', 'Parking Services'),
                     ('Public Relations Services', 'Public Relations Services')]


def all_flags(code):
    """it get the flag of the country according to the country's alpha code """
    if code == 'AD':
        return '🇦🇩'
    elif code == 'AE':
        return '🇦🇪'
    elif code == 'AF':
        return '🇦🇫'
    elif code == 'AG':
        return '🇦🇬'
    elif code == 'AI':
        return '🇦🇮'
    elif code == 'AL':
        return '🇦🇱'
    elif code == 'AM':
        return '🇦🇲'
    elif code == 'AO':
        return '🇦🇴'
    elif code == 'AQ':
        return '🇦🇶'
    elif code == 'AR':
        return '🇦🇷'
    elif code == 'AS':
        return '🇦🇸'
    elif code == 'AT':
        return '🇦🇹'
    elif code == 'AU':
        return '🇦🇺'
    elif code == 'AW':
        return '🇦🇼'
    elif code == 'AX':
        return '🇦🇽'
    elif code == 'AZ':
        return '🇦🇿'
    elif code == 'BA':
        return '🇧🇦'
    elif code == 'BB':
        return '🇧🇧'
    elif code == 'BD':
        return '🇧🇩'
    elif code == 'BE':
        return '🇧🇪'
    elif code == 'BF':
        return '🇧🇫'
    elif code == 'BG':
        return '🇧🇬'
    elif code == 'BH':
        return '🇧🇭'
    elif code == 'BI':
        return '🇧🇮'
    elif code == 'BJ':
        return '🇧🇯'
    elif code == 'BL':
        return '🇧🇱'
    elif code == 'BM':
        return '🇧🇲'
    elif code == 'BN':
        return '🇧🇳'
    elif code == 'BO':
        return '🇧🇴'
    elif code == 'BQ':
        return '🇧🇶'
    elif code == 'BR':
        return '🇧🇷'
    elif code == 'BS':
        return '🇧🇸'
    elif code == 'BT':
        return '🇧🇹'
    elif code == 'BV':
        return '🇧🇻'
    elif code == 'BW':
        return '🇧🇼'
    elif code == 'BY':
        return '🇧🇾'
    elif code == 'BZ':
        return '🇧🇿'
    elif code == 'CA':
        return '🇨🇦'
    elif code == 'CC':
        return '🇨🇨'
    elif code == 'CD':
        return '🇨🇩'
    elif code == 'CF':
        return '🇨🇫'
    elif code == 'CG':
        return '🇨🇬'
    elif code == 'CH':
        return '🇨🇭'
    elif code == 'CI':
        return '🇨🇮'
    elif code == 'CK':
        return '🇨🇰'
    elif code == 'CL':
        return '🇨🇱'
    elif code == 'CM':
        return '🇨🇲'
    elif code == 'CN':
        return '🇨🇳'
    elif code == 'CO':
        return '🇨🇴'
    elif code == 'CR':
        return '🇨🇷'
    elif code == 'CU':
        return '🇨🇺'
    elif code == 'CV':
        return '🇨🇻'
    elif code == 'CW':
        return '🇨🇼'
    elif code == 'CX':
        return '🇨🇽'
    elif code == 'CY':
        return '🇨🇾'
    elif code == 'CZ':
        return '🇨🇿'
    elif code == 'DE':
        return '🇩🇪'
    elif code == 'DJ':
        return '🇩🇯'
    elif code == 'DK':
        return '🇩🇰'
    elif code == 'DM':
        return '🇩🇲'
    elif code == 'DO':
        return '🇩🇴'
    elif code == 'DZ':
        return '🇩🇿'
    elif code == 'EC':
        return '🇪🇨'
    elif code == 'EE':
        return '🇪🇪'
    elif code == 'EG':
        return '🇪🇬'
    elif code == 'EH':
        return '🇪🇭'
    elif code == 'ER':
        return '🇪🇷'
    elif code == 'ES':
        return '🇪🇸'
    elif code == 'ET':
        return '🇪🇹'
    elif code == 'FI':
        return '🇫🇮'
    elif code == 'FJ':
        return '🇫🇯'
    elif code == 'FK':
        return '🇫🇰'
    elif code == 'FM':
        return '🇫🇲'
    elif code == 'FO':
        return '🇫🇴'
    elif code == 'FR':
        return '🇫🇷'
    elif code == 'GA':
        return '🇬🇦'
    elif code == 'GB':
        return '🇬🇧'
    elif code == 'GD':
        return '🇬🇩'
    elif code == 'GE':
        return '🇬🇪'
    elif code == 'GF':
        return '🇬🇫'
    elif code == 'GG':
        return '🇬🇬'
    elif code == 'GH':
        return '🇬🇭'
    elif code == 'GI':
        return '🇬🇮'
    elif code == 'GL':
        return '🇬🇱'
    elif code == 'GM':
        return '🇬🇲'
    elif code == 'GN':
        return '🇬🇳'
    elif code == 'GP':
        return '🇬🇵'
    elif code == 'GQ':
        return '🇬🇶'
    elif code == 'GR':
        return '🇬🇷'
    elif code == 'GS':
        return '🇬🇸'
    elif code == 'GT':
        return '🇬🇹'
    elif code == 'GU':
        return '🇬🇺'
    elif code == 'GW':
        return '🇬🇼'
    elif code == 'GY':
        return '🇬🇾'
    elif code == 'HK':
        return '🇭🇰'
    elif code == 'HM':
        return '🇭🇲'
    elif code == 'HN':
        return '🇭🇳'
    elif code == 'HR':
        return '🇭🇷'
    elif code == 'HT':
        return '🇭🇹'
    elif code == 'HU':
        return '🇭🇺'
    elif code == 'ID':
        return '🇮🇩'
    elif code == 'IE':
        return '🇮🇪'
    elif code == 'IL':
        return '🇮🇱'
    elif code == 'IM':
        return '🇮🇲'
    elif code == 'IN':
        return '🇮🇳'
    elif code == 'IO':
        return '🇮🇴'
    elif code == 'IQ':
        return '🇮🇶'
    elif code == 'IR':
        return '🇮🇷'
    elif code == 'IS':
        return '🇮🇸'
    elif code == 'IT':
        return '🇮🇹'
    elif code == 'JE':
        return '🇯🇪'
    elif code == 'JM':
        return '🇯🇲'
    elif code == 'JO':
        return '🇯🇴'
    elif code == 'JP':
        return '🇯🇵'
    elif code == 'KE':
        return '🇰🇪'
    elif code == 'KG':
        return '🇰🇬'
    elif code == 'KH':
        return '🇰🇭'
    elif code == 'KI':
        return '🇰🇮'
    elif code == 'KM':
        return '🇰🇲'
    elif code == 'KN':
        return '🇰🇳'
    elif code == 'KP':
        return '🇰🇵'
    elif code == 'KR':
        return '🇰🇷'
    elif code == 'KW':
        return '🇰🇼'
    elif code == 'KY':
        return '🇰🇾'
    elif code == 'KZ':
        return '🇰🇿'
    elif code == 'LA':
        return '🇱🇦'
    elif code == 'LB':
        return '🇱🇧'
    elif code == 'LC':
        return '🇱🇨'
    elif code == 'LI':
        return '🇱🇮'
    elif code == 'LK':
        return '🇱🇰'
    elif code == 'LR':
        return '🇱🇷'
    elif code == 'LS':
        return '🇱🇸'
    elif code == 'LT':
        return '🇱🇹'
    elif code == 'LU':
        return '🇱🇺'
    elif code == 'LV':
        return '🇱🇻'
    elif code == 'LY':
        return '🇱🇾'
    elif code == 'MA':
        return '🇲🇦'
    elif code == 'MC':
        return '🇲🇨'
    elif code == 'MD':
        return '🇲🇩'
    elif code == 'ME':
        return '🇲🇪'
    elif code == 'MF':
        return '🇲🇫'
    elif code == 'MG':
        return '🇲🇬'
    elif code == 'MH':
        return '🇲🇭'
    elif code == 'MK':
        return '🇲🇰'
    elif code == 'ML':
        return '🇲🇱'
    elif code == 'MM':
        return '🇲🇲'
    elif code == 'MN':
        return '🇲🇳'
    elif code == 'MO':
        return '🇲🇴'
    elif code == 'MP':
        return '🇲🇵'
    elif code == 'MQ':
        return '🇲🇶'
    elif code == 'MR':
        return '🇲🇷'
    elif code == 'MS':
        return '🇲🇸'
    elif code == 'MT':
        return '🇲🇹'
    elif code == 'MU':
        return '🇲🇺'
    elif code == 'MV':
        return '🇲🇻'
    elif code == 'MW':
        return '🇲🇼'
    elif code == 'MX':
        return '🇲🇽'
    elif code == 'MY':
        return '🇲🇾'
    elif code == 'MZ':
        return '🇲🇿'
    elif code == 'NA':
        return '🇳🇦'
    elif code == 'NC':
        return '🇳🇨'
    elif code == 'NE':
        return '🇳🇪'
    elif code == 'NF':
        return '🇳🇫'
    elif code == 'NG':
        return '🇳🇬'
    elif code == 'NI':
        return '🇳🇮'
    elif code == 'NL':
        return '🇳🇱'
    elif code == 'NO':
        return '🇳🇴'
    elif code == 'NP':
        return '🇳🇵'
    elif code == 'NR':
        return '🇳🇷'
    elif code == 'NU':
        return '🇳🇺'
    elif code == 'NZ':
        return '🇳🇿'
    elif code == 'OM':
        return '🇴🇲'
    elif code == 'PA':
        return '🇵🇦'
    elif code == 'PE':
        return '🇵🇪'
    elif code == 'PF':
        return '🇵🇫'
    elif code == 'PG':
        return '🇵🇬'
    elif code == 'PH':
        return '🇵🇭'
    elif code == 'PK':
        return '🇵🇰'
    elif code == 'PL':
        return '🇵🇱'
    elif code == 'PM':
        return '🇵🇲'
    elif code == 'PN':
        return '🇵🇳'
    elif code == 'PR':
        return '🇵🇷'
    elif code == 'PS':
        return '🇵🇸'
    elif code == 'PT':
        return '🇵🇹'
    elif code == 'PW':
        return '🇵🇼'
    elif code == 'PY':
        return '🇵🇾'
    elif code == 'QA':
        return '🇶🇦'
    elif code == 'RE':
        return '🇷🇪'
    elif code == 'RO':
        return '🇷🇴'
    elif code == 'RS':
        return '🇷🇸'
    elif code == 'RU':
        return '🇷🇺'
    elif code == 'RW':
        return '🇷🇼'
    elif code == 'SA':
        return '🇸🇦'
    elif code == 'SB':
        return '🇸🇧'
    elif code == 'SC':
        return '🇸🇨'
    elif code == 'SD':
        return '🇸🇩'
    elif code == 'SE':
        return '🇸🇪'
    elif code == 'SG':
        return '🇸🇬'
    elif code == 'SH':
        return '🇸🇭'
    elif code == 'SI':
        return '🇸🇮'
    elif code == 'SJ':
        return '🇸🇯'
    elif code == 'SK':
        return '🇸🇰'
    elif code == 'SL':
        return '🇸🇱'
    elif code == 'SM':
        return '🇸🇲'
    elif code == 'SN':
        return '🇸🇳'
    elif code == 'SO':
        return '🇸🇴'
    elif code == 'SR':
        return '🇸🇷'
    elif code == 'SS':
        return '🇸🇸'
    elif code == 'ST':
        return '🇸🇹'
    elif code == 'SV':
        return '🇸🇻'
    elif code == 'SX':
        return '🇸🇽'
    elif code == 'SY':
        return '🇸🇾'
    elif code == 'SZ':
        return '🇸🇿'
    elif code == 'TC':
        return '🇹🇨'
    elif code == 'TD':
        return '🇹🇩'
    elif code == 'TF':
        return '🇹🇫'
    elif code == 'TG':
        return '🇹🇬'
    elif code == 'TH':
        return '🇹🇭'
    elif code == 'TJ':
        return '🇹🇯'
    elif code == 'TK':
        return '🇹🇰'
    elif code == 'TL':
        return '🇹🇱'
    elif code == 'TM':
        return '🇹🇲'
    elif code == 'TN':
        return '🇹🇳'
    elif code == 'TO':
        return '🇹🇴'
    elif code == 'TR':
        return '🇹🇷'
    elif code == 'TT':
        return '🇹🇹'
    elif code == 'TV':
        return '🇹🇻'
    elif code == 'TW':
        return '🇹🇼'
    elif code == 'TZ':
        return '🇹🇿'
    elif code == 'UA':
        return '🇺🇦'
    elif code == 'UG':
        return '🇺🇬'
    elif code == 'UM':
        return '🇺🇲'
    elif code == 'US':
        return '🇺🇸'
    elif code == 'UY':
        return '🇺🇾'
    elif code == 'UZ':
        return '🇺🇿'
    elif code == 'VA':
        return '🇻🇦'
    elif code == 'VC':
        return '🇻🇨'
    elif code == 'VE':
        return '🇻🇪'
    elif code == 'VG':
        return '🇻🇬'
    elif code == 'VI':
        return '🇻🇮'
    elif code == 'VN':
        return '🇻🇳'
    elif code == 'VU':
        return '🇻🇺'
    elif code == 'WF':
        return '🇼🇫'
    elif code == 'WS':
        return '🇼🇸'
    elif code == 'XK':
        return '🇽🇰'
    elif code == 'YE':
        return '🇾🇪'
    elif code == 'YT':
        return '🇾🇹'
    elif code == 'ZA':
        return '🇿🇦'
    elif code == 'ZM':
        return '🇿🇲'
    return '🏳'
