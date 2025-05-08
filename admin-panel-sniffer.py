#!/usr/bin/env python
#import required modules
from datetime import datetime as dt
import sys, random, optparse, time, os
try:#python 3
    import urllib.request as req
    from urllib.error import URLError, HTTPError
    three = True
except ImportError:#python 2
    import urllib2 as req
    three = False

#custom header to avoid being blocked by the website
custom_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT {}; rv:{}.0) Gecko/20100101 Firefox/{}.0".format(random.randint(7,11),
                                                                                                           random.randint(40,50),
                                                                                                           random.randint(35,50))}

def adjustDomainName(domain):#correct domain name for urllib
    if domain.startswith("www."):
        domain = domain[4:]
    if not domain.startswith("http"):
        domain = "http://" + domain
    if domain.endswith("/"):
        domain = domain[:-1]
    return domain

def loadWordList(wordlist_file, ext):#load pages to check from dictionary
    try:
        with open(wordlist_file, encoding="utf8") as wlf:
            content = wlf.readlines()
        for i in range(len(content)):
            content[i] = content[i].strip("\n")
        if ext.lower() == "a":
            return content
        else:
            return [element for element in content if element.endswith(ext) or element.endswith("/")]
    except FileNotFoundError:
        sys.exit("Couldn't find wordlist file!")

def saveResults(file_name, found_pages, progress=0):
    now = dt.now()
    with open("admin_sniffer_results.txt", "a") as f:
        stamp = "%d-%d-%d %d: %d: %d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        print(stamp, file=f)
        for page in found_pages:
            print(page, file=f)
        print("total progress: %d\n______________________________________________" % progress, file=f)

def main(domain, progress=0, ext="a", strict=False, save=True, visible=True, wordlist_file="admin_login.txt"):
    print(" [+] HULK Is On Progress... Feel Free To Press Ctrl+C At Any Point To Abort...")
    resp_codes = {403 : "request forbidden", 401 : "authentication required"}#HTTP response codes
    found = []#list to hold the results we find
    domain = adjustDomainName(domain)#correct domain name for urllib

    print(" [+] Loading Wordlist...")
    attempts = loadWordList(wordlist_file, ext)
    print(" [+] Crawling...")
    
    for link in attempts[progress:]:#loop over every page in the wordlist file
        try:
            site = domain + "/" + link

            if visible:#show links as they're being tested
                print(" trying:", end=" ")

            panel_page = req.Request(site, headers=custom_headers)
            
            try:
                resp = req.urlopen(site)#try visiting the page
                found.append(site)
                print(" ✔️✔️✔️ " "%s page valid!" % site)

            except HTTPError as e:#investigate the HTTPError we got
                if three:
                    c = e.getcode()
                else:
                    c = e.code()
                    
                if c == 404:
                    if visible:
                        print("%s not found..." % site)
                else:
                    print("%s potential positive.. %s" % (site, resp_codes[c]))
                    if not strict:
                        found.append(site)

            except URLError:
                print("invalid link or no internet connection!")
                break
            
            except Exception as e2:
                print("an exception occured when trying {}... {}".format(site, e2))
                continue
            progress += 1
            
        except KeyboardInterrupt:#make sure we don't lose everything should the user get bored
            print()
            break

    if found:
        if save:#save results to a text file
            print("Saving results...")
            saveResults("admin_sniffer_results.txt", found)

            print("results saved to admin_sniffer_results.txt...")

        print("found the following results: " + "  ".join(found) + " total progress: %s" % progress)

    else:
        print("could not find any panel pages... Make sure you're connected to the internet\n" \
              + "or try a different wordlist. total progress: %s" % progress)

def getRobotsFile(domain):
    print("Attempting to get robots.txt file...")
    found = []
    domain = adjustDomainName(domain)#correct domain name for urllib
    
    robots_file = domain + "/robots.txt"
    try:
        data = req.urlopen(robots_file).read().decode("utf-8")
        for element in data.split("\n"):
            if element.startswith("Disallow:"):
                panel_page = domain + element[10:]
                print("Disallow rule found: %s" % (panel_page))
                found.append(panel_page)
        if found:
            print("admin panels found... Saving results to file...")
            saveResults("admin_sniffer_results.txt", found, 0)
            print("done...")
        else:
            print("could not find any panel pages in the robots file...")
    except:
        sys.exit("Could not retrieve robots.txt!")

# Helper functions for printing
def slowprint(text):
    for c in text + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(10. / 100)

def bannerprint(text):
    for c in text + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(100000. / 10000000)

# Main execution block
if __name__ == "__main__":
    try:
        # Clear screen and show banner
        os.system('cls' if os.name == 'nt' else 'clear')
        slowprint("\033[91m************* Screen Loading For You *************** ")
        
        banner = '''\033[92m
  _                                          
 (_)___                                      
 | (_-<                   v.2.O                   
 |_/__/ _    _                               
   | |_| |_ (_)___                           
   |  _| ' \| (_-<            _       _      
  _ \__|_||_|_/__/_   __ _ __| |_ __ (_)_ _  
 | || / _ \ || | '_| / _` / _` | '  \| | ' \ 
  \_, \___/\_,_|_|   \__,_\__,_|_|_|_|_|_||_|
  |__/        Admin Panel Finder                                
  github page : https://github.com/SamiAlshamaly
  Created by: sami khatatba
'''
        bannerprint(banner)
        slowprint(" [!] RESPECT OTHER'S PRIVACY ")
        time.sleep(1)
        
        # Interactive mode
        use_interactive = True
        
        # Check if command line arguments were provided
        if len(sys.argv) > 1:
            # Set up command line options
            parser = optparse.OptionParser("Usage: python %prog --domain <target domain> " \
                                        + "--progress <index of the page the script reached last run> " \
                                        + "--page_extension <website language> --strict <True or False> " \
                                        + "--save <Save the results to a text file?> " \
                                        + "--verbose <print links as they're tested?> --wordlist <dictionary file to use>" \
                                        + "--robots <if True don't enter anything else except the domain name>")

            domain_help = "target domain. eg: google.com or www.example.org"
            progress_help = "(optional) index of the page the script reached last run. The script " \
                            + "displays and saves this value in the results file after every run. "\
                            + "0 starts from the beginning."
            page_extension_help = "(optional) whether the website uses html asp php... default value is 'a' which checks everything"
            strict_mode_help = "(optional, default False) if True, HTTP codes that correspond to forbidden or " \
                            + "authentication required will be ignored."
            save_help = "(optional, default True) if True results will be saved to a txt file."
            verbose_help = "(optional, default True) if True each link will be shown as it's being tested."
            wordlist_help = "(optional, default is the included wordlist) wordlist file to be used."
            robots_help = "(optional, default False) if True the script will try to get the robots.txt " \
                        + "file that usually contains the admin panel. If you set it to True, don't enter" \
                        + "anything else except the target domain."

            parser.add_option("--domain", dest="domain", type="string", help=domain_help)
            parser.add_option("--progress", dest="progress", type="string", help=progress_help)
            parser.add_option("--page_extension", dest="page_ext", type="string", help=page_extension_help)
            parser.add_option("--strict", dest="strict", type="string", help=strict_mode_help)
            parser.add_option("--save", dest="save", type="string", help=save_help)
            parser.add_option("--verbose", dest="verbose", type="string", help=verbose_help)
            parser.add_option("--wordlist", dest="wordlist", type="string", help=wordlist_help)
            parser.add_option("--robots", dest="robots", type="string", help=robots_help)

            (options, args) = parser.parse_args()
            
            if options.domain:
                use_interactive = False
                
                # Set default values for options
                strict_mode = False
                if options.strict:
                    try:
                        strict_mode = eval(options.strict.title())
                    except:
                        pass

                save = True
                if options.save:
                    try:
                        save = eval(options.save.title())
                    except:
                        pass

                verbose = True
                if options.verbose:
                    try:
                        verbose = eval(options.verbose.title())
                    except:
                        pass

                page_ext = 'a'
                if options.page_ext:
                    page_ext = options.page_ext

                progress = 0
                if options.progress:
                    try:
                        progress = int(options.progress)
                    except:
                        pass

                wordlist = "admin_login.txt"
                if options.wordlist:
                    wordlist = options.wordlist

                robots = False
                if options.robots:
                    try:
                        robots = eval(options.robots.title())
                    except:
                        pass

                # Execute the main functionality
                if robots:
                    getRobotsFile(options.domain)
                else:
                    main(options.domain, progress, page_ext, strict_mode, save, verbose, wordlist)
        
        # Interactive mode
        if use_interactive:
            print("\n\033[93m===== Interactive Mode =====\033[0m")
            
            # Get domain from user
            domain = input("\n\033[96m[+] Enter target domain (e.g., example.com): \033[0m").strip()
            
            # Get wordlist option
            use_custom_wordlist = input("\n\033[96m[+] Use custom wordlist? (y/n): \033[0m").strip().lower()
            
            if use_custom_wordlist == 'y':
                wordlist = input("\n\033[96m[+] Enter path to wordlist file: \033[0m").strip()
                # Check if wordlist exists
                if not os.path.isfile(wordlist):
                    print(f"\n\033[91m[!] Wordlist file '{wordlist}' not found. Using default wordlist.\033[0m")
                    wordlist = "admin_login.txt"
            else:
                wordlist = "admin_login.txt"
            
            # Get page extension
            use_specific_ext = input("\n\033[96m[+] Filter by specific page extension? (y/n): \033[0m").strip().lower()
            
            if use_specific_ext == 'y':
                page_ext = input("\n\033[96m[+] Enter page extension (e.g., php, html): \033[0m").strip()
            else:
                page_ext = 'a'
            
            # Get robots.txt option
            check_robots = input("\n\033[96m[+] Check robots.txt file? (y/n): \033[0m").strip().lower()
            
            # Additional options
            print("\n\033[93m===== Advanced Options =====\033[0m")
            print("\033[92m[*] Press Enter to use default values\033[0m")
            
            # Strict mode
            strict_input = input("\n\033[96m[+] Use strict mode? (y/n) [default: n]: \033[0m").strip().lower()
            strict_mode = True if strict_input == 'y' else False
            
            # Save results
            save_input = input("\n\033[96m[+] Save results to file? (y/n) [default: y]: \033[0m").strip().lower()
            save = False if save_input == 'n' else True
            
            # Verbose mode
            verbose_input = input("\n\033[96m[+] Show verbose output? (y/n) [default: y]: \033[0m").strip().lower()
            verbose = False if verbose_input == 'n' else True
            
            print("\n\033[93m===== Starting Scan =====\033[0m")
            
            # Execute based on user choices
            if check_robots == 'y':
                getRobotsFile(domain)
            else:
                main(domain, 0, page_ext, strict_mode, save, verbose, wordlist)
            
    except KeyboardInterrupt:
        print("\n [-] Ctrl + C Detected \n")
    
    try:
        input(" [+] Enter To Exit ")
        slowprint("\n\033[91m [+] Exiting.... Thanks For Using My Tool  \n")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
    except KeyboardInterrupt:
        print("\n\033[90m [-] See You Again ^-^ ")
