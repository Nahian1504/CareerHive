import requests
from bs4 import BeautifulSoup
from .models import Job

# Adzuna API credentials
ADZUNA_APP_ID = "a93f1680"
ADZUNA_APP_KEY = "191b1bdf3d77c3807084f01667a37b7d"

def scrape_indeed(keyword="python developer", location="remote"):
    url = f"https://www.indeed.com/jobs?q={keyword}&l={location}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for job_card in soup.find_all("a", class_="tapItem"):
        title = job_card.find("h2").text.strip() if job_card.find("h2") else "N/A"
        company = job_card.find("span", class_="companyName").text.strip() if job_card.find("span", class_="companyName") else "N/A"
        location = job_card.find("div", class_="companyLocation").text.strip() if job_card.find("div", class_="companyLocation") else "N/A"
        link = "https://www.indeed.com" + job_card.get("href")
        jobs.append({"title": title, "company": company, "location": location, "link": link, "source": "Indeed"})

    return jobs

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
        print("Error fetching Adzuna jobs:", e)
    return jobs

def get_jobs(keyword="python developer", location="remote"):
    """Combine jobs from multiple sources."""
    jobs = []
    jobs += scrape_indeed(keyword, location)
    jobs += fetch_adzuna(keyword)
    # We can add more sources here in the future
    return jobs