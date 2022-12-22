from tkinter import ttk
import tkinter as tk
import pyperclip
import json
import requests
from dateutil.parser import parse
from bs4 import BeautifulSoup
from threading import Timer

root = tk.Tk()
root.title('Currency Converter')
root.iconbitmap('icon.ico')
root.geometry('300x500')
root.resizable(False, False)

frame_from_currency = tk.Frame(root, background='#37AAFD', height=250)
frame_to_currency = tk.Frame(root, background='white', height=250)
select_frame = tk.Frame(root)

frame_from_currency.pack(fill='x')
frame_to_currency.pack(fill='x')

search_event = False
update_offline = True
list_to_forgot = []
list_to_forgot2 = []


def update_offline_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    data = requests.get(url).json()
    text_file = open("rates.txt", "w")
    text_file.write(str(data))
    text_file.close()


def convert_offline(from_currency, to_currency, amount):
    f = open('rates.txt', 'r')
    data = json.loads(str(f.read()).replace("'", '"'))
    if data["result"] == "success":
        last_updated_datetime = parse(data["time_last_update_utc"])
        last_updated = str(last_updated_datetime).split(' ')[0]
        exchange_rates = data["rates"]
    initial_amount = amount
    if from_currency != 'EUR':
        amount = amount / exchange_rates[from_currency]

    # limiting the precision to 2 decimal places
    amount = round(amount * exchange_rates[to_currency], 2)
    return amount, last_updated


def before_convert():
    if len(entry_from.get()) != 0:
        button_border.place_forget()
        entry_to.config(state='normal')
        entry_to.delete(0, 'end')
        entry_to.insert(0, 'Account in progress..')
        entry_to.config(state='disabled')
        start_other_frame = Timer(0, convert_currency)
        start_other_frame.start()


def convert_currency():
    global update_offline
    fromC_upper = from_currency_button['text']
    toC_upper = to_currency_button['text']
    qty = entry_from.get()
    try:
        last_update_lable.configure(text='')
        offline.configure(text='')
        url = f"https://www.xe.com/currencyconverter/convert/?Amount={qty}&From={fromC_upper}&To={toC_upper}"
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        result_code = soup.findAll('p', {"class": "result__BigRate-sc-1bsijpp-1 iGrAod"})[0].decode_contents()
        result = str(result_code).split('<')
        entry_to.config(state='normal')
        entry_to.delete(0, 'end')
        entry_to.insert(0, str(result[0]))
        entry_to.config(state='disabled')
        button_border.place(relx=0.5, rely=0.65, anchor='center')
        if update_offline:
            update_offline_rates()
            update_offline = False
    except Exception as e:
        try:
            result, last_update = convert_offline(str(fromC_upper), str(toC_upper), int(qty))
            entry_to.config(state='normal')
            entry_to.delete(0, 'end')
            entry_to.insert(0, str(result))
            entry_to.config(state='disabled')
            offline.place(relx=0.5, rely=0.8, anchor='center')
            last_update_lable.configure(text='last update : '+str(last_update))
            offline.configure(text='Offline Mode')
        except:
            entry_to.config(state='normal')
            entry_to.delete(0, 'end')
            entry_to.insert(0, 'Currency not found')
            entry_to.config(state='disabled')


def callback(action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
    if len(str(prior_value)) == 0 and str(text) == ".":
        return False
    if len(entry_from.get()) > 20:
        if str(action) == "0":
            return True
        else:
            return False
    if str.isdigit(text) or value_if_allowed == "" or str(text) == ".":
        if str(prior_value).__contains__('.') and str(text) == "." and str(action) != '0':
            return False
        else:
            return True
    else:
        return False


def copy_to_keyboard():
    data = entry_to.get()
    pyperclip.copy(str(data))


def select_event(w):
    global text_from
    global text_to
    global search_event
    search_event = True
    if str(w) == 'from':
        text_from = True
        text_to = False
    elif str(w) == 'to':
        text_to = True
        text_from = False
    search.pack()
    Entry_border.pack(anchor='nw', padx=4)
    Entry_border_back.place(relx=0.89, rely=0.02,anchor='center')
    back_button.pack()
    select_frame.pack(fill=tk.BOTH)
    convert_button_border.place_forget()
    frame_from_currency.pack_forget()
    frame_to_currency.pack_forget()


def get_items(e):
    global search_event
    search_event = False
    widget_name = str(e.widget.cget("text")).split('\n')
    currency_name = str(widget_name[1]).replace('(', '').replace(')', '')
    if text_from:
        from_currency_button.configure(text=str(currency_name))
    elif text_to:
        to_currency_button.configure(text=str(currency_name))
    search.delete(0, tk.END)
    Entry_border_back.place_forget()
    search.pack_forget()
    Entry_border.pack_forget()
    select_frame.pack_forget()
    convert_button_border.place(relx=0.5, rely=0.5, anchor='center')
    frame_from_currency.pack(fill='x')
    frame_to_currency.pack(fill='x')


def back_event(e):
    global search_event
    if search_event:
        search.delete(0, tk.END)
        Entry_border.pack_forget()
        Entry_border_back.place_forget()
        search.pack_forget()
        Entry_border.pack_forget()
        select_frame.pack_forget()
        convert_button_border.place(relx=0.5, rely=0.5, anchor='center')
        frame_from_currency.pack(fill='x')
        frame_to_currency.pack(fill='x')
        search_event = False


def search_function(e):
    if len(search.get()) != 0:
        for items_to_forgot in list_to_forgot:
            globals()[items_to_forgot].pack_forget()
            list_to_forgot.remove(str(items_to_forgot))
        for items_to_forgot2 in list_to_forgot2:
            globals()[items_to_forgot2].pack_forget()
        new_sorted_search = sorted(currency.items(), key=lambda kv: (kv[1], kv[0]))
        for curr_search in new_sorted_search:
            if str(search.get()).lower() in str(curr_search).lower():
                globals()['button_border_search_' + str(curr_search[0])] = tk.Frame(my_frame_auto,
                                                                                    highlightbackground="#37AAFD",
                                                                                    highlightthickness=2, bd=0)
                globals()[curr_search[0]] = tk.Button(globals()['button_border_search_' + str(curr_search[0])],
                                                      text=curr_search[1] + '\n' + f'({curr_search[0]})',
                                                      font=('Arial', 12, 'bold'),
                                                      background='white', bd=0, fg='#37AAFD', width=27, height=3)
                globals()[curr_search[0]].bind("<Button-1>", get_items)
                globals()[curr_search[0]].pack(anchor='nw')
                globals()['button_border_search_' + str(curr_search[0])].pack(pady=2, padx=2)
                list_to_forgot.append(curr_search[0])
                if list_to_forgot2.__contains__('button_border_search_' + str(curr_search[0])):
                    pass
                else:
                    list_to_forgot2.append('button_border_search_' + str(curr_search[0]))
        my_canvas_auto.configure(scrollregion=my_canvas_auto.bbox('all'))


wrapper1_auto = tk.LabelFrame(select_frame, background='white')
my_canvas_auto = tk.Canvas(wrapper1_auto, width=280, height=500, background='white')
my_frame_auto = tk.Frame(my_canvas_auto, background='white')

Entry_border = tk.Frame(root, highlightbackground="#37AAFD", highlightthickness=2, bd=0)
search = tk.Entry(Entry_border, width=25, font=('Arial', 12, 'bold'), highlightbackground="black", highlightthickness=2,
                  bd=0)
Entry_border_back = tk.Frame(root, highlightbackground="#37AAFD", highlightthickness=0, bd=0)
back_button = tk.Label(Entry_border_back, text='←', font=('Arial', 20, 'bold'), bd=0, width=2, height=1)
back_button.bind('<Button-1>', back_event)
search.bind("<KeyRelease>", search_function)

currency = {'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar',
            'JPY': 'Japanese Yen',
            'INR': 'Indian Rupee',
            'NZD': 'New Zealand Dollar',
            'CHF': 'Swiss Franc',
            'ZAR': 'South African Rand',
            'RUB': 'Russian Ruble',
            'BGN': 'Bulgarian Lev',
            'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar',
            'SEK': 'Swedish Krona',
            'THB': 'Thai Baht',
            'HUF': 'Hungarian Forint',
            'CNY': 'Chinese Yuan Renminbi',
            'NOK': 'Norwegian Krone',
            'MXN': 'Mexican Peso',
            'DKK': 'Danish Krone',
            'MYR': 'Malaysian Ringgit',
            'PLN': 'Polish Zloty',
            'BRL': 'Brazilian Real',
            'PHP': 'Philippine Peso',
            'IDR': 'Indonesian Rupiah',
            'CZK': 'Czech Koruna',
            'AED': 'Emirati Dirham',
            'TWD': 'Taiwan New Dollar',
            'KRW': 'South Korean Won',
            'ILS': 'Israeli Shekel',
            'ARS': 'Argentine Peso',
            'CLP': 'Chilean Peso',
            'EGP': 'Egyptian Pound',
            'TRY': 'Turkish Lira',
            'RON': 'Romanian Leu',
            'SAR': 'Saudi Arabian Riyal',
            'PKR': 'Pakistani Rupee',
            'COP': 'Colombian Peso',
            'IQD': 'Iraqi Dinar',
            'XAU': 'Gold Ounce',
            'FJD': 'Fijian Dollar',
            'KWD': 'Kuwaiti Dinar',
            'BAM': 'Bosnian Convertible Mark',
            'ISK': 'Icelandic Krona',
            'MAD': 'Moroccan Dirham',
            'HRK': 'Croatian Kuna',
            'VND': 'Vietnamese Dong',
            'JMD': 'Jamaican Dollar',
            'JOD': 'Jordanian Dinar',
            'DOP': 'Dominican Peso',
            'PEN': 'Peruvian Sol',
            'CRC': 'Costa Rican Colon',
            'BHD': 'Bahraini Dinar',
            'BDT': 'Bangladeshi Taka',
            'DZD': 'Algerian Dinar',
            'KES': 'Kenyan Shilling',
            'XAG': 'Silver Ounce',
            'LKR': 'Sri Lankan Rupee',
            'OMR': 'Omani Rial',
            'QAR': 'Qatari Riyal',
            'XOF': 'CFA Franc',
            'IRR': 'Iranian Rial',
            'XCD': 'East Caribbean Dollar',
            'TND': 'Tunisian Dinar',
            'TTD': 'Trinidadian Dollar',
            'XPF': 'CFP Franc',
            'EEK': 'Estonian Kroon',
            'ZMK': 'Zambian Kwacha',
            'ZMW': 'Zambian Kwacha',
            'BBD': 'Barbadian or Bajan Dollar',
            'NGN': 'Nigerian Naira',
            'LBP': 'Lebanese Pound',
            'XAF': 'Central African CFA Franc',
            'MUR': 'Mauritian Rupee',
            'XPT': 'Platinum Ounce',
            'BSD': 'Bahamian Dollar',
            'ALL': 'Albanian Lek',
            'UYU': 'Uruguayan Peso',
            'BMD': 'Bermudian Dollar',
            'LVL': 'Latvian Lat',
            'UAH': 'Ukrainian Hryvnia',
            'GTQ': 'Guatemalan Quetzal',
            'XDR': 'IMF Special Drawing Rights',
            'BWP': 'Botswana Pula',
            'BOB': 'Bolivian Bolíviano',
            'CUP': 'Cuban Peso',
            'PYG': 'Paraguayan Guarani',
            'HNL': 'Honduran Lempira',
            'LTL': 'Lithuanian Litas',
            'ZWD': 'Zimbabwean Dollar',
            'NIO': 'Nicaraguan Cordoba',
            'RSD': 'Serbian Dinar',
            'NPR': 'Nepalese Rupee',
            'HTG': 'Haitian Gourde',
            'PAB': 'Panamanian Balboa',
            'SVC': 'Salvadoran Colon',
            'GYD': 'Guyanese Dollar',
            'KYD': 'Caymanian Dollar',
            'TZS': 'Tanzanian Shilling',
            'CNH': 'Chinese Yuan Renminbi Offshore',
            'CVE': 'Cape Verdean Escudo',
            'FKP': 'Falkland Island Pound',
            'ANG': 'Dutch Guilder',
            'UGX': 'Ugandan Shilling',
            'MGA': 'Malagasy Ariary',
            'GEL': 'Georgian Lari',
            'ETB': 'Ethiopian Birr',
            'MDL': 'Moldovan Leu',
            'VUV': 'Ni-Vanuatu Vatu',
            'SYP': 'Syrian Pound',
            'BND': 'Bruneian Dollar',
            'KHR': 'Cambodian Riel',
            'NAD': 'Namibian Dollar',
            'MKD': 'Macedonian Denar',
            'AOA': 'Angolan Kwanza',
            'PGK': 'Papua New Guinean Kina',
            'MMK': 'Burmese Kyat',
            'KZT': 'Kazakhstani Tenge',
            'MOP': 'Macau Pataca',
            'MZN': 'Mozambican Metical',
            'LYD': 'Libyan Dinar',
            'SLL': 'Sierra Leonean Leone',
            'GNF': 'Guinean Franc',
            'BYN': 'Belarusian Ruble',
            'BYR': 'Belarusian Ruble',
            'GMD': 'Gambian Dalasi',
            'AWG': 'Aruban or Dutch Guilder',
            'AMD': 'Armenian Dram',
            'YER': 'Yemeni Rial',
            'LAK': 'Lao Kip',
            'WST': 'Samoan Tala',
            'MWK': 'Malawian Kwacha',
            'KPW': 'North Korean Won',
            'BIF': 'Burundian Franc',
            'DJF': 'Djiboutian Franc',
            'MNT': 'Mongolian Tughrik',
            'UZS': 'Uzbekistani Som',
            'TOP': "Tongan Pa'anga",
            'SCR': 'Seychellois Rupee',
            'KGS': 'Kyrgyzstani Som',
            'BTN': 'Bhutanese Ngultrum',
            'SBD': 'Solomon Islander Dollar',
            'GIP': 'Gibraltar Pound',
            'RWF': 'Rwandan Franc',
            'CDF': 'Congolese Franc',
            'MVR': 'Maldivian Rufiyaa',
            'MRU': 'Mauritanian Ouguiya',
            'ERN': 'Eritrean Nakfa',
            'SOS': 'Somali Shilling',
            'SZL': 'Swazi Lilangeni',
            'TJS': 'Tajikistani Somoni',
            'LRD': 'Liberian Dollar',
            'LSL': 'Basotho Loti',
            'SHP': 'Saint Helenian Pound',
            'STN': 'Sao Tomean Dobra',
            'KMF': 'Comorian Franc',
            'SPL': 'Seborgan Luigino',
            'TMT': 'Turkmenistani Manat',
            'SRD': 'Surinamese Dollar',
            'IMP': 'Isle of Man Pound',
            'JEP': 'Jersey Pound',
            'TVD': 'Tuvaluan Dollar',
            'GGP': 'Guernsey Pound',
            'AFN': 'Afghan Afghani',
            'AZN': 'Azerbaijan Manat',
            'BZD': 'Belizean Dollar',
            'CUC': 'Cuban Convertible Peso',
            'GHS': 'Ghanaian Cedi',
            'SDG': 'Sudanese Pound',
            'VES': 'Venezuelan Bolívar',
            'VEF': 'Venezuelan Bolívar',
            'XPD': 'Palladium Ounce',
            'BTC': 'Bitcoin',
            'ADA': 'Cardano',
            'BCH': 'Bitcoin Cash',
            'DOGE': 'Dogecoin',
            'DOT': 'Polkadot',
            'ETH': 'Ethereum',
            'LINK': 'Chainlink',
            'LTC': 'Litecoin',
            'LUNA': 'Terra',
            'UNI': 'Uniswap',
            'XLM': 'Stellar Lumen',
            'XRP': 'Ripple',
            'ATS': 'Austrian Schilling',
            'AZM': 'Azerbaijani Manat',
            'BEF': 'Belgian Franc',
            'CYP': 'Cypriot Pound',
            'DEM': 'German Deutsche Mark',
            'ESP': 'Spanish Peseta',
            'FIM': 'Finnish Markka',
            'FRF': 'French Franc',
            'GHC': 'Ghanaian Cedi',
            'GRD': 'Greek Drachma',
            'IEP': 'Irish Pound',
            'ITL': 'Italian Lira',
            'LUF': 'Luxembourg Franc',
            'MGF': 'Malagasy Franc',
            'MRO': 'Mauritanian Ouguiya',
            'MTL': 'Maltese Lira',
            'MZM': 'Mozambican Metical',
            'NLG': 'Dutch Guilder',
            'PTE': 'Portuguese Escudo',
            'ROL': 'Romanian Leu',
            'SDD': 'Sudanese Dinar',
            'SIT': 'Slovenian Tolar',
            'SKK': 'Slovak Koruna',
            'SRG': 'Surinamese Guilder',
            'STD': 'Sao Tomean Dobra',
            'TMM': 'Turkmenistani Manat',
            'TRL': 'Turkish Lira',
            'VAL': 'Vatican City Lira',
            'VEB': 'Venezuelan Bolívar',
            'XEU': 'European Currency Unit'}
print(len(currency))
new_sorted = sorted(currency.items(), key=lambda kv: (kv[1], kv[0]))
for curr in new_sorted:
    globals()['button_border_search_' + str(curr[0])] = tk.Frame(my_frame_auto, highlightbackground="#37AAFD",
                                                                 highlightthickness=2, bd=0)
    globals()[curr[0]] = tk.Button(globals()['button_border_search_' + str(curr[0])],
                                   text=curr[1] + '\n' + f'({curr[0]})', font=('Arial', 12, 'bold'),
                                   background='white', bd=0, fg='#37AAFD', width=27, height=3)
    globals()[curr[0]].bind("<Button-1>", get_items)
    globals()[curr[0]].pack(anchor='nw')
    globals()['button_border_search_' + str(curr[0])].pack(pady=2, padx=2)
    list_to_forgot.append(curr[0])
    list_to_forgot2.append('button_border_search_' + str(curr[0]))
y_scrollbar_auto = ttk.Scrollbar(wrapper1_auto, orient='vertical', command=my_canvas_auto.yview)
my_canvas_auto.bind('<Configure>', lambda e: my_canvas_auto.configure(scrollregion=my_canvas_auto.bbox('all')))
my_canvas_auto.configure(yscrollcommand=y_scrollbar_auto.set)
my_canvas_auto.create_window((0, 0), window=my_frame_auto, anchor="nw")
my_canvas_auto.pack(side=tk.LEFT, fill='both')
y_scrollbar_auto.pack(side=tk.RIGHT, fill="both")
wrapper1_auto.pack(fill=tk.X, expand=tk.YES)

canvas = tk.Canvas(frame_from_currency, width=230, height=30, background='#37AAFD')
canvas.place(relx=0.5, rely=0.5, anchor='center')

canvas = tk.Canvas(frame_to_currency, width=230, height=30, background='#37AAFD')
canvas.place(relx=0.5, rely=0.5, anchor='center')

vcmd = (root.register(callback))
entry_from = tk.Entry(frame_from_currency, background='#37AAFD', width=20, bd=0, highlightthickness=0,
                      font=('Arial', 16, 'bold'), justify='center', validate='all',
                      validatecommand=(vcmd, '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))
entry_from.place(relx=0.5, rely=0.5, anchor='center')
entry_to = tk.Entry(frame_to_currency, background='white', width=20, bd=0, highlightthickness=0,
                    font=('Arial', 16, 'bold'), justify='center')
entry_to.place(relx=0.5, rely=0.5, anchor='center')
entry_to.config(state='disabled', disabledbackground="white")

from_currency_button = tk.Button(frame_from_currency, text='USD', font=('Arial', 12, 'bold'), background='#37AAFD',
                                 bd=0, fg='white', command=lambda: select_event('from'))
from_currency_button.place(relx=0.5, rely=0.35, anchor='center')

to_currency_button = tk.Button(frame_to_currency, text='EUR', font=('Arial', 12, 'bold'), background='white', bd=0,
                               fg='#37AAFD', command=lambda: select_event('to'))
to_currency_button.place(relx=0.5, rely=0.35, anchor='center')

convert_button_border = tk.Frame(root, highlightbackground="#37AAFD", highlightthickness=2, bd=0)
convert_button = tk.Button(convert_button_border, text='Convert', fg='black', bg='white', font=('Arial', 15, 'bold'),
                           bd=0, command=before_convert, width=15, activebackground='white')
convert_button.pack()
convert_button_border.place(relx=0.5, rely=0.5, anchor='center')

button_border = tk.Frame(frame_to_currency, highlightbackground="#37AAFD", highlightthickness=2, bd=0)
bttn = tk.Button(button_border, text='Copy Result', fg='black', bg='white', bd=0,
                 command=copy_to_keyboard)
bttn.pack()
button_border.place(relx=0.5, rely=0.65, anchor='center')

root.bind('<Escape>', back_event)

last_update_lable = tk.Label(frame_to_currency, font=("Arial", 10, 'bold'), background='white', foreground='black')
offline = tk.Label(frame_to_currency, font=("Arial", 10, 'bold'), background='white', foreground='red')
last_update_lable.place(relx=0.5, rely=0.9, anchor='center')
button_border.place(relx=0.5, rely=0.65, anchor='center')
root.mainloop()
