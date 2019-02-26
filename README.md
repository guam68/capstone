# Proposal

## Background

Keyforge is a card game designed by Richard Garfield (designer of Magic: The Gathering) and published by Fantasy Flight Games (FFG). It was released on November 15th 2018 and has already seen over 600k decks registered despite supply chain issues. One of the main points of interest of this game is that every deck is procedurally generated and guaranteed to be 100% unique in its card composition. This was implementated in part to prevent the formation of a meta where only a certain subset of cards are found in decks at competitive events. Players will always seek out a way to "solve the meta" though, and two prominent systems, ADHD and SAS, have been developed to aid players in evaluating the strength of a deck.


## Overview

Unlike the current rating systems, this project aims at viewing a decks "relavance", for lack of a better term, in the current meta as opposed to determining its raw strengths. Decks will be filtered by composition and compared against the top performing decks to find its current likelyhood to be a "meta deck". A visual will also be displayed showing the decks with most similar compositions and the "strength" (as win/loss ratio) of those decks. This may allow players to gain insight on a particular deck composition's potential without even having to play it. Other figures such as global deck statistic comparisions, deck composition breakdown, and other information useful to a user will also be diplayed.

To track decks for competitive play, FFG has implemented a deck registration system that ensures all deck information will be available online. Keyforgegame.com uses an undocumented API to populate its website with that data for global searches and individual deck information. This API will be leveraged to create a database for the project as well as being used for on demand updating to ensure the most relavant data is being shown to the user. 

This project will use D3.js for all of its data visualization. Vue.js is an option for the frontend but it will ultimately depend on the amount of time available. PostgreSQL will be used for the database with Django as the web framework.


## Functionality

When first visiting the site, a user will be presented with an input form to generate a deck search. This search will either route the user to the detail page if the search is specific enough or present them with a list of possible links based on the search parameter. 

Information regarding organized play may be out of date due to the way data is collected for the database. Once the user is redirected to the detail page, the keyforge API should be called for the searched deck as well as the decks displayed in the *similar composition* visual. This data will be used to populate the page where necessary as well as update the database for those decks. Using this system, specific deck info will always be the most up to date information with global and top deck data lagging behind by at most a day(ideally).

Once on the deck detail page, the user will be presented with the information and visuals for that specific deck. This information should include:

- Deck composition broken down by house. This should be a list that includes a hover effect to show an image of the actual card
- Graph of distribution for card types (Action, Artifact, Creature, Upgrade)
- Graph of distribution for creature power
- Graph of global deck comparisons
    - One for each card type
    - Bonus aember
    - Win/loss ratio
    - Organized Play games played
    - Chains
- Graphs of top x% (based on power level and win %) comparisions. Will include all the same categories as global
- Rating based on composition of deck vs most frequently occuring cards by house within *"meta"* decks (possibly weighted with respect to card rarity?)
- Visualization of decks most similar in composition
    - Consists of a series of nodes that represent decks
    - Node size will represent the % match in composition
    - Node color will represent the win % of the deck
    - User should be able to interact with nodes (click or hover) to display additional information by either linking to the deck's detail page, displaying info in a modal, or something similar


## Data Model

- **deck**
    - name: text
    - expansion: integer
    - power_level: integer
    - chains: integer
    - wins: integer
    - losses: integer
    - id: text (primary key)
- **deck_card**
    - deck_id: text (foreign key: deck)  
    - card_id: text (foreign key: card)
- **deck_house**
    - deck_id: text (foreign key: deck)
    - house: text
- **card**
    - id: text (primary key)
    - card_title: text
    - house: text
    - card_type: text
    - front_image: text
    - card_text: text
    - traits: text
    - amber: integer
    - power: integer
    - armor: integer
    - rarity: text
    - flavor_text: text
    - card_number: integer
    - expansion: integer
    - is_maverick: boolean


## Schedule

### Week 1

- [x] Basic html elements for site (home + detail pages)
- [x] Get basic search working
- [x] Get raw data to detail page

### Week 2

- [ ] Bar graphs for all data
- [ ] Basic force-directed graph (fdg) for similar deck comp visual

### Week 3

- [ ] Interaction and information for fdg nodes
- [ ] Make site look less ugly

### Post Class

- [ ] Auto data collection
- [ ] Better search + filters
- [ ] More prettier
- [ ] Deploy site
_________________________
- [ ] Web scraper for SAS, AERC, and ADHD ratings
- [ ] API for others to access everything
_________________________
- [ ] User login system
- [ ] User profile page
- [ ] User saved decks
