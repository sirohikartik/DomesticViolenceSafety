# Create a Domestic Violence Safety Platform


## Requirment Analysis

### Functional Requirements 

## Features
1. Ability to report any episode of domestic violence
2. Provide emergency helpline
3. Maybe record audio during episode by permission of the user?
4. Use AI to record audio locally and flag potential episodes??
5. With permission of user report to concerned authorities

## Technicals
1. Have an app? (yes)
2. Ability to login or signup
3. Give permission to record audio
4. Analyse audio and listen for potential problems/episodes
5. Report to authority 
6. provide ai support (chatbot) (Hive reporting?)
7. Authorities also use the app
so we have the normal victims and people from authority that u can reach out to in case of issues that u are facing and it analyzes live audio(locally) and looks for signs of episodes or issues and reports to an authority member who is reponsible for the block/area. 

## Specifications
1. Backend infrastructure for user handling
2. Local ai system for privacy of audio  
3. Flag potential episodes -- collect data for a specific amount of time or look for patterns also give that pattern statistic to the authority.

###### This can be borderline spying but we have to keep it local so it doesn't become a cause for concern, the private nature of the application/software must be maintained.


## Technical Specifications

1. Neon DB database
2. FastAPI/ Golang backend
3. Flutter App/ React Native app
4. OpenRouter LLMs or local LLM for MVP (to maintian privacy) -> for support chatbot
5. Tensorflow lite based audio analysis model for recognising violent activity


### Non-Functional Requirements

###### Backend doesn't need to have high end system we just need to maintain a lot of data about the users.
###### Main functionality will be on the client's machine. so we are going for a client heavy architecture.

##### Backend needs to be live 24 times 7 

# Domain Classes 


#### People

1. Victims/normal users
2. people who work at some authority (who is responsible for this)
3. admins who control the system
4. Potentially police members associated with the responsibility of the application.

#### Places

1. Divided into blocks based on user's location.
2. Country -> state -> district -> block 

#### Things

1. None


#### Organizations 

1. Domestic Violence Safety Organizations 
2. Police/ law inforcement agencies 
3. NGOs

#### Concepts

1. Domestic Violence Recognization Factors
2. Causes and Effects of reporting

etc


#### Events

1. Episode :  A domestic violence recognized incident or reported incident
2. Reporting to authorities
