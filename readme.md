<div align="center">
<h1 align="center">
<img src="https://kboll.s3.amazonaws.com/projects/reader/favicon@1x.png" width="100" />
<br>archive-reader-backend</h1>
<h3>Use this app to build, connect and perform operations on the database for the archive reader application - the source code for which can be found <a href="https://github.com/kylebollinger/archive-reader">https://github.com/kylebollinger/archive-reader</a></h3>
<h3>Developed with the software and tools below.</h3>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/NumPy-013243.svg?style&logo=NumPy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Markdown-000000.svg?style&logo=Markdown&logoColor=white" alt="Markdown" />
</p>
<img src="https://img.shields.io/github/last-commit/kylebollinger/archive-reader-backend?style&color=5D6D7E" alt="git-last-commit" />
<img src="https://img.shields.io/github/commit-activity/m/kylebollinger/archive-reader-backend?style&color=5D6D7E" alt="GitHub commit activity" />
<img src="https://img.shields.io/github/languages/top/kylebollinger/archive-reader-backend?style&color=5D6D7E" alt="GitHub top language" />
</div>

---

## 📖 Table of Contents
- [📖 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [📂 Repository Structure](#-repository-structure)
- [⚙️ Modules](#modules)
- [🚀 Getting Started](#-getting-started)
    - [🔧 Installation](#-installation)
    - [🤖 Running archive-reader-backend](#-running-archive-reader-backend)
- [🛣 Roadmap](#-roadmap)

---


## 📍 Overview


With a USB drive of nearly 80,000 individual HTML pages of ancient text chapters, I decided to build an app that organizes the entire library. For more information about this project check out the [full writeup](https://kylebollinger.dev/projects/archive-texts) on my protfolio site.

This is how the backend will be setup. The database for the reader app is simple but accounts for the variance in all the books.

![ERD diagrom of the backend design for the library](https://kboll.s3.amazonaws.com/projects/reader/back/db-diagram.webp)
ERD diagrom of the backend design for the library

---


## 📂 Repository Structure

```sh
└── archive-reader-backend/
    ├── db/
    │   ├── cleaners.py
    │   ├── exports.py
    │   └── models.py
    ├── requirements.txt
    ├── run.py
    └── scraper/
        ├── processors.py
        ├── scrapers.py
        └── utils.py
```


---

## ⚙️ Modules

<details open><summary>Root</summary>

| File                                                                                                   | Summary |
| ---                                                                                                    | --- |
| [requirements.txt](https://github.com/kylebollinger/archive-reader-backend/blob/main/requirements.txt) | App Dependencies |
| [run.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/run.py)                     | Import and execute various functions for cleaning and exporting data from the db |

</details>

<details closed><summary>Db</summary>

| File                                                                                            | Summary |
| ---                                                                                             | --- |
| [exports.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/db/exports.py)   | Functions to export data from the db to a local file |
| [models.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/db/models.py)     | SQL Alchemy wrapper for defining models and establishing db connection |
| [cleaners.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/db/cleaners.py) | Functions to perform direct db operations to clean data post scraping |

</details>

<details closed><summary>Scraper</summary>

| File                                                                                                     | Summary                   |
| ---                                                                                                      | ---                       |
| [scrapers.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/scraper/scrapers.py)     | BeautifulSoup scraper functions |
| [processors.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/scraper/processors.py) | Functions for post-processing raw scraper data |
| [utils.py](https://github.com/kylebollinger/archive-reader-backend/blob/main/scraper/utils.py)           | Utility functions for various app operations |

</details>

---

## 🚀 Getting Started

***Dependencies***

Please ensure you have the following dependencies installed on your system:

`- ℹ️ Python 3.11`


### 🔧 Installation

1. Clone the archive-reader-backend repository:
```sh
git clone https://github.com/kylebollinger/archive-reader-backend
```

2. Change to the project directory:
```sh
cd archive-reader-backend
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🤖 Running archive-reader-backend

Make sure you define the db connection in .env file. Choose an operation to run from the run.py file and then execute:
```sh
python run.py
```


## 🛣 Roadmap

> - [ ] `ℹ️  Add infinite scrolling to the reader`
> - [ ] `ℹ️  Expand the library with more texts from new sources`
> - [ ] `ℹ️  Use AI (Midjourney, Dalle, etc) to generate book cover art for texts that dont have one`


---

## 🤝 Contributing

Contributions are always welcome! Please follow these steps:
1. Fork the project repository. This creates a copy of the project on your account that you can modify without affecting the original project.
2. Clone the forked repository to your local machine using a Git client like Git or GitHub Desktop.
3. Create a new branch with a descriptive name (e.g., `new-feature-branch` or `bugfix-issue-123`).
```sh
git checkout -b new-feature-branch
```
4. Make changes to the project's codebase.
5. Commit your changes to your local branch with a clear commit message that explains the changes you've made.
```sh
git commit -m 'Implemented new feature.'
```
6. Push your changes to your forked repository on GitHub using the following command
```sh
git push origin new-feature-branch
```
7. Create a new pull request to the original project repository. In the pull request, describe the changes you've made and why they're necessary.
The project maintainers will review your changes and provide feedback or merge them into the main branch.

---
