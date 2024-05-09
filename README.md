# Patreon Post to Epub converter

This is a quick and dirty selenium based script to go and capture all of 
the html posts in chronological order for a tag, then turn them into an epub.  
Editing the script will allow you to use it for additional communities.

## Usage
Create a yaml file for stories:
```
---
creator:
  name: patreonname
stories:
  - Walls
  - College Stories
  - WIP
blacklist:
  - Taking a Break
  - Thank you
```

Use `patreon.py --help` to get command usage information.

Either `-c` or `-f` are required, this will tell the script which browser
selenium should be trying to control.  The `username` and `password` fields
are your patreon username and password, oauth is not supported.

## Setup

These steps are assuming you're using a virtual environment.  Start a shell:  powershell on windows, or bash/zsh on mac/linux.

```shell
$ python -m venv .venv
$ . .venv/bin/activate 
$ pip install -r ../requirements.txt
$ 
```
If you're on windows this is `.venv/Scripts/` instead of being `.venv/bin/`.
In windows you may need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` before activating.

At this point you now need to configure the link between selenium (WebDriver)
and your browser.  Follow the steps at 
https://selenium-python.readthedocs.io/installation.html#drivers to configure. 
 You can place the exe file for firefox or chrome in `.venv/bin` or 
 `.venv/Scripts` as long as you use the activate script to add the 
 virtual environment to your path.

You can now go back to your shell and run `python patreon.py --help` or read 
the usage to run the script.

# Converting to other formats.

Epub is a open standard, and a good starting point, if you need a book in almost
any other ebook/document format, your best bet is to download 
[Calibre](https://calibre-ebook.com/) and then use the 
[ebook-convert](https://manual.calibre-ebook.com/generated/en/ebook-convert.html) command.

```
ebook-convert Walls.epub Walls.pdf
```