# === libs ===

import pickle # store date
import os # create new folders
from urllib.request import urlopen # open URLs
from bs4 import BeautifulSoup # BeautifulSoup; parsing HTML
import re # regex; extract substrings
import time # delay execution; calculate script's run time
from datetime import datetime # add IDs to files/folders' names
from alive_progress import alive_bar # progress bar
import webbrowser # open browser
import ssl # fix certificate issue: https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate
import certifi # fix certificate issue: https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate
from sys import platform # check platform (Windows/Linux/macOS)
if platform == 'win32':
    from win10toast_persist import ToastNotifier # Windows 10 notifications
    # TODO: open URL on click // https://stackoverflow.com/questions/62828043/how-to-perform-a-function-when-toast-notification-is-clicked-in-python
    toaster = ToastNotifier() # initialize win10toast
    # from termcolor import colored # colored input/output in terminal
elif platform == 'darwin':
    import pync # macOS notifications 
import requests # for IFTTT integration / webhook to send emails

# === start + run time ===

start = time.time() # run time start
print("Starting...")

# === have current date in exported files' names ===

# https://www.w3schools.com/python/python_datetime.asp
today_date = datetime.strftime(datetime.now(), '%y%m%d_%f') # YYMMDD_microsecond

filename = 'date.pk'
try: # might crash on first run
    # load your data back to memory so we can save new value; NOTE: b = binary
    with open(filename, 'rb') as file:
        previous_date = pickle.load(file) # keep previous_date (last time the script ran) in a file so we can retrieve it later and compare / diff files 
        print("Previous date:", previous_date) 
except IOError:
    print("First run - no file exists.") # if it's the first time script is running we won't have the file created so we skip  

try:
    with open(filename, 'wb') as file: # open pickle file
        pickle.dump(today_date, file) # dump today_date (the time script is running) into the file so then we can use it to compare / diff files
        print("Today date: ", today_date) 
except IOError:
    print("File doesn't exist.")

# create new YYMMDD_microsecond folder
if not os.path.isdir("/output/" + today_date):
    os.mkdir("output/" + today_date) # example: 211220_123456
    print("Folder created: " + today_date)

# === URLs to scrape ===

# BMW, 140+ KM, AT, PDC, AC, Xen, Pb/On, 18.5k PLN, Częstochowa + 250 km, sort: newest
page_url = "https://www.otomoto.pl/osobowe/bmw/czestochowa/?search%5Bfilter_float_price%3Ato%5D=18500&search%5Bfilter_enum_fuel_type%5D%5B0%5D=petrol&search%5Bfilter_enum_fuel_type%5D%5B1%5D=diesel&search%5Bfilter_float_engine_power%3Afrom%5D=140&search%5Bfilter_enum_gearbox%5D%5B0%5D=automatic&search%5Bfilter_enum_gearbox%5D%5B1%5D=cvt&search%5Bfilter_enum_gearbox%5D%5B2%5D=dual-clutch&search%5Bfilter_enum_gearbox%5D%5B3%5D=semi-automatic&search%5Bfilter_enum_gearbox%5D%5B4%5D=automatic-stepless-sequential&search%5Bfilter_enum_gearbox%5D%5B5%5D=automatic-stepless&search%5Bfilter_enum_gearbox%5D%5B6%5D=automatic-sequential&search%5Bfilter_enum_gearbox%5D%5B7%5D=automated-manual&search%5Bfilter_enum_gearbox%5D%5B8%5D=direct-no-gearbox&search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_features%5D%5B0%5D=rear-parking-sensors&search%5Bfilter_enum_features%5D%5B1%5D=automatic-air-conditioning&search%5Bfilter_enum_features%5D%5B2%5D=xenon-lights&search%5Bfilter_enum_features%5D%5B3%5D=cruise-control&search%5Bfilter_enum_no_accident%5D=1&search%5Border%5D=created_at_first%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bdist%5D=250&search%5Bcountry%5D="

# === IFTTT integration === 

filename2 = 'imk.pk'
try: # might crash on first run
    # load your data back to memory so we can save new value; NOTE: b = binary
    with open(filename2, 'rb') as file:
        ifttt_maker_key = pickle.load(file)
except IOError:
    print("First run - no file exists.")

event_name = 'new-car-otomoto'
webhook_url = f'https://maker.ifttt.com/trigger/{event_name}/with/key/{ifttt_maker_key}'

def run_ifttt_automation(url):
    report = {}
    report["value1"] = url
    # report["value2"] = second
    # report["value3"] = third
    requests.post(webhook_url, data=report)

# === function to scrape data ===

def pullData(page_url):

    # ? can't crawl too often? works better with Otomoto limits perhaps
    pause_duration = 3 # seconds to wait
    print("Waiting for", pause_duration, "seconds before opening URL...")
    with alive_bar(pause_duration, bar="circles", spinner="dots_waves") as bar:
        for second in range(0, pause_duration):
            time.sleep(1)
            bar()

    print("Opening page...")
    # print (page_url) # debug 
    page = urlopen(page_url, context=ssl.create_default_context(
        cafile=certifi.where())) # fix certificate issue

    print("Scraping page...")
    soup = BeautifulSoup(page, 'html.parser') # parse the page

    # 'a' (append) to add lines to existing file vs overwriting
    with open(r"output/" + today_date + "/1-output.txt", "a", encoding="utf-8") as bs_output:
        # print (colored("Creating local file to store URLs...", 'green')) # colored text on Windows
        counter = 0 # counter to get # of URLs/cars
        with alive_bar(bar="classic2", spinner="classic") as bar: # progress bar
            for link in soup.find_all("a", {"class": "offer-title__link"}):
                bs_output.write(link.get('href'))
                counter += 1 # counter ++
                bar() # progress bar ++
                # print ("Adding", counter, "URL to file...")
        print("Successfully added", counter, "cars to file.")

# === run URLs in function ^ ===

try:
    open(r"output/" + today_date + "/1-output.txt",
         "w").close() # clean main file at start
except: # crashes on 1st run when file is not yet created
    print("Nothing to clean, moving on...")

# number_of_pages_to_crawl = int(input("Ile podstron chcesz przejrzeć? >>> ")) # give user choice
number_of_pages_to_crawl = 2

page_number = 1 # begin at page=1
for page in range(1, number_of_pages_to_crawl+1):
    print("Page number:", page_number, "/",
          number_of_pages_to_crawl) 
    full_page_url = f"{page_url}{page_number}"
    pullData(full_page_url)
    page_number += 1 # go to next page

# === make file more pretty by adding new lines ===

with open(r"output/" + today_date + "/1-output.txt", "r", encoding="utf-8") as scraping_output_file: # open file...
    print("Reading file to clean up...")
    read_scraping_output_file = scraping_output_file.read() # ... and read it

urls_line_by_line = re.sub(r"#[a-zA-Z0-9]+(?!https$)://|https://|#[a-zA-Z0-9]+", "\n", read_scraping_output_file) # add new lines; remove IDs at the end of URL, eg '#e5c6831089'

urls_line_by_line = urls_line_by_line.replace("www", "https://www") # make text clickable again

print("Cleaning the file...")

carList = urls_line_by_line.split() # remove "\n"; add to list
uniqueCarList = list(set(carList)) # remove duplicates 

print("File cleaned up. New lines added.")

with open(r"output/" + today_date + "/2-clean.txt", "w", encoding="utf-8") as clean_file:
    for element in sorted(uniqueCarList): # sort URLs
        clean_file.write("%s\n" % element) # write to file

# === tailor the results by using a keyword: brand, model (possibly also engine size etc) ===

# regex_user_input = input("Jak chcesz zawęzić wyniki? Możesz wpisać markę (np. BMW) albo model (np. E39) >>> ") # for now using brand as quesion but user can put any one-word keyword
regex_user_input = ""
if len(regex_user_input) == 0:
    print("Keyword wasn't provided - not searching.")
else: 
    regex_user_input = regex_user_input.strip() # strip front & back
    print("Opening file to search for keyword:", regex_user_input)
    reg = re.compile(regex_user_input) # matches "KEYWORD" in lines
    counter2 = 0 # another counter to get the # of search results
    with open(r'output/' + today_date + '/3-search_keyword.txt', 'w') as output: # open file for writing
        print("Searching for keyword...")
        with open(r'output/' + today_date + '/2-clean.txt', 'r', encoding='UTF-8') as clean_no_dupes_file: # look for keyword in the clean file without empty lines and duplicates 
            with alive_bar(bar="circles", spinner="dots_waves") as bar:
                for line in clean_no_dupes_file: # read file line by line
                    if reg.search(line): # if there is a match anywhere in a line
                        output.write(line) # write the line into the new file
                        counter2 += 1 # counter ++
                        bar() # progress bar ++
                        # print ("Progress:", counter2)
            if counter2 == 1:
                print("Found", counter2, "result.")
                # if platform == "win32":
                #     toaster.show_toast("otomoto-scraper", "Found " + str(counter2) +
                #                        " result.",  icon_path="icons/www.ico", duration=None)
            else:
                print("Found", counter2, "results.")
                # if platform == "win32":
                #     toaster.show_toast("otomoto-scraper", "Found " + str(counter2) +
                #                        " results.",  icon_path="icons/www.ico", duration=None)

# === open keyword/search results ^ in browser ===

    if counter2 != 0:
        # user_choice_open_urls = input("Chcesz otworzyć linki w przeglądarce? [y/n] >>> ")
        user_choice_open_urls = 'n'
        if user_choice_open_urls == 'y':
            with open(r'" + today_date + "/3-search_keyword.txt', 'r', encoding='UTF-8') as search_results:
                counter3 = 0
                print("Opening URLs in browser...")
                with alive_bar(bar="circles", spinner="dots_waves") as bar:
                    for line in search_results: # go through the file
                        webbrowser.open(line) # open URL in browser
                        counter3 += 1
                        bar()
            if counter3 != 1: # correct grammar for multiple (URLs; them; they)
                print("Opened ", str(counter3),
                    " URLs in the browser. Go and check them before they go 404 ;)")
                # if platform == "win32":
                #     toaster.show_toast("otomoto-scraper", "Opened " + str(counter3) +
                #                        " URLs.",  icon_path="icons/www.ico", duration=None)
            else: # correct grammar for 1 (URL; it)
                print("Opened", counter3,
                    "URL in the browser. Go and check it before it goes 404 ;)")
                # if platform == "win32":
                #     toaster.show_toast("otomoto-scraper", "Opened " + str(counter3) +
                #                        " URL.",  icon_path="icons/www.ico", duration=None)
        else:
            # print ("Ok - URLs saved in 'output/search-output.txt' anyway.")
            print("Ok - URLs saved to a file.")
            # print("Script run time:", datetime.now()-start)
            # sys.exit()
    else:
        print("No search results found.")

# === compare files === 

try:
    counter2
except NameError:
    print("Variable not defined. Keyword wasn't provided.") 

    try:
        file_previous_run = open('output/' + previous_date + '/2-clean.txt', 'r') # 1st file 
        file_current_run = open('output/' + today_date + '/2-clean.txt', 'r') # 2nd file 

        f1 = [x for x in file_previous_run.readlines()] # set with lines from 1st file  
        f2 = [x for x in file_current_run.readlines()] # set with lines from 2nd file 

        diff = [line for line in f1 if line not in f2] # lines present only in 1st file 
        diff1 = [line for line in f2 if line not in f1] # lines present only in 2nd file 
        # *NOTE file2 must be > file1

        if len(diff1) == 0: # check if set is empty - if it is then there are no differences between files 
            print('Files are the same.')
            if platform == "darwin":
                    pync.notify('Nie ma nowych aut.', title='otomoto', contentImage="https://i.postimg.cc/t4qh2n6V/car.png") # appIcon="" doesn't work, using contentImage instead
            elif platform == "win32":
                toaster.show_toast(title="otomoto", msg='Nie ma nowych aut.', icon_path="icons/car.ico", duration=None, threaded=True) # duration=None - leave notification in Notification Center; threaded=True - rest of the script will be allowed to be executed while the notification is still active
        else:
            with open('diff/diff-' + today_date + '.txt', 'w') as w:
                counter4 = 0 # counter 
                for url in diff1: # go piece by piece through the differences 
                    w.write(url) # write to file
                    run_ifttt_automation(url) # run IFTTT automation with URL
                    counter4 += 1 # counter++
            if counter4 <= 0: # should not fire 
                print ('No new cars since last run.')
                if platform == "darwin":
                    pync.notify('Nie ma nowych aut.', title='otomoto', contentImage="https://i.postimg.cc/t4qh2n6V/car.png") # appIcon="" doesn't work, using contentImage instead
                elif platform == "win32":
                    toaster.show_toast(title="otomoto", msg='Nie ma nowych aut.', icon_path="icons/car.ico", duration=None, threaded=True) # duration=None - leave notification in Notification Center; threaded=True - rest of the script will be allowed to be executed while the notification is still active
            else:
                print (counter4, "new cars found since last run! Go check them now!")
                if platform == "darwin":
                    pync.notify(f'Nowe auta: {counter4}', title='otomoto', open=page_url, contentImage="https://i.postimg.cc/t4qh2n6V/car.png", sound="Funk") # appIcon="" doesn't work, using contentImage instead
                elif platform == "win32":
                    toaster.show_toast(title="otomoto", msg=f'Nowe auta: {counter4}', icon_path="icons/car.ico", duration=None, threaded=True) # duration=None - leave notification in Notification Center; threaded=True - rest of the script will be allowed to be executed while the notification is still active
                    time.sleep(5)
                    webbrowser.open(page_url)
                
    except IOError:
        print("No previous data - can't diff.")

else:
    print("Keyword was provided; search was successful.") 
    # TODO: same as above but with /[x]-search_keyword.txt

# === run time ===

# run_time = datetime.now()-start
end = time.time() # run time end 
run_time = round(end-start,2)
print("Script run time:", run_time, "seconds.")