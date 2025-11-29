import requests
from bs4 import BeautifulSoup
import time  

# API KEYS 
ADZUNA_APP_ID = "a93f1680"
ADZUNA_APP_KEY = "191b1bdf3d77c3807084f01667a37b7d"
USAJOBS_API_KEY = "hMJLm6PCFkzY9ZcvzMBhHvS+xUCUxURp7R8ah5NwuYU="
AFFID = "18dbea833b67d7565a350fa79ef7b735"

# INDEED SCRAPER 
def scrape_indeed(keyword="python developer", location="remote"):
    url = f"https://www.indeed.com/jobs?q={keyword}&l={location}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"} 
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        
        for job_card in soup.find_all("a", class_="tapItem"):  
            title = job_card.find("h2").text.strip() if job_card.find("h2") else "N/A"
            company = job_card.find("span", class_="companyName").text.strip() if job_card.find("span", class_="companyName") else "N/A"
            location_elem = job_card.find("div", class_="companyLocation")
            location = location_elem.text.strip() if location_elem else "N/A"
            link = "https://www.indeed.com" + job_card.get("href") if job_card.get("href") else "N/A"
            jobs.append({"title": title, "company": company, "location": location, "link": link, "source": "Indeed"})
        
        time.sleep(2)  
        return jobs
    except Exception as e:
        print(f"Indeed scraping failed: {e}")
        return [] 

# ADZUNA 
def fetch_adzuna(keyword="python developer"):
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "what": keyword,
        "content-type": "application/json"
    }
    jobs = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        for job in data.get("results", []):
            link = job.get("redirect_url") or job.get("ad_url")
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "location": job.get("location", {}).get("display_name"),
                "link": link,
                "source": "Adzuna"
            })
    except Exception as e:
        print(f"Error fetching Adzuna jobs: {e}")
    return jobs

# USAJOBS 
def fetch_usajobs(keyword="python developer", location=""):
    url = "https://data.usajobs.gov/api/search"
    headers = {
        "User-Agent": "nahian.tasnim@slu.edu",  
        "X-Api-Key": USAJOBS_API_KEY  
    }
    params = {
        "Keyword": keyword,
        "LocationName": location,
        "ResultsPerPage": 50,
        "Page": 1
    }
    jobs = []
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  
        data = response.json()
        for item in data.get("SearchResult", {}).get("SearchResultItems", []):
            desc = item.get("MatchedObjectDescriptor", {})
            jobs.append({
                "title": desc.get("PositionTitle", "N/A"),
                "company": desc.get("OrganizationName", "USAJobs"),
                "location": desc.get("PositionLocationDisplay", "Unknown"),
                "link": desc.get("PositionURI", ""),
                "source": "USAJobs"
            })
    except Exception as e:
        print(f"USAJobs request failed: {e}")
    return jobs

# CAREERJET 
def fetch_careerjet_jobs(keywords="python developer", location="remote", pagesize=50, page=1):
    url = "http://public.api.careerjet.net/search"
    params = {
        "affid": AFFID,
        "keywords": keywords,
        "location": location,
        "pagesize": pagesize,
        "page": page,
        "user_ip": "127.0.0.1",
        "user_agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        jobs = []
        for job in data.get("jobs", []):
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("locations"),
                "link": job.get("url"),
                "source": "CareerJet"
            })
        return jobs
    except Exception as e:
        print(f"Error fetching CareerJet jobs: {e}")
        return []

# COMBINE ALL SOURCES
def get_jobs(keyword="python developer", location="remote"):
    jobs = []
    try:
        jobs += scrape_indeed(keyword, location)
    except Exception as e:
        print(f"Indeed failed: {e}")
    
    try:
        jobs += fetch_adzuna(keyword)
    except Exception as e:
        print(f"Adzuna failed: {e}")
    
    try:
        jobs += fetch_usajobs(keyword, location)
    except Exception as e:
        print(f"USAJobs failed: {e}")
    
    try:
        jobs += fetch_careerjet_jobs(keywords=keyword, location=location) 
    except Exception as e:
        print(f"CareerJet failed: {e}")
    
    return jobs
