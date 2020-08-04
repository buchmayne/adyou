# ADYou #

### Introduction ###

An online platform designed to improve homeowners' experience in developing accessory dwelling units. The first version of the software will be unique to the Portland Metro region. The aim of the product is to provide value to homeowners who are interested in the potential of building an ADU. As of now the product will have two distinct features. The first being an analytics dashboard that provides insights into the feasibility and financial implications of ADU development. By applying concepts from real estate finance and urban economics users will be able to identify potential returns on their investment. Second, the platform will provide valuable information related to the ADU construction process. This feature doesn't seek to be a substitute for a general contractor or other construction professional, but rather a guide rail to help homeowners better understand the ADU construction process, and work with construction professionals more efficiently. The goal of the software would be to provide more than general information, and deliver insights unique to each homeowners' property. For example, homeowners could be prompted to input the number of trees in their back yard and the distance between the trees, for which the software would identify possible tree related issues with respect to development. Again, the motivation here is to not automate away the input and expertise of professionals but to better inform homeowners to work more efficently with professionals. 

* Analytics to inform the decision making process of whether or not a homeowner should build an ADU

* Tailored information regarding the ADU process to help homeowners have a better experience in the construction of their ADU

Another hypothetical feature would be to incorporate additional information regarding financing opportunities for the ADU development process. Not sure if there is currently anyway to provide value add with this feature and still bootstrap this project.  

### Data Sources ###

* RLIS -- parcel data and assessors information

* Development Professional Expertise -- will be required to tailor the ADU proforma

* Redfin // Craigslist // Facebook Marketplace -- Will need to scrape data to create database of ADUs for sale and for rent

* CoStar -- create multifamily rent surface to identify what potential ADU rent might be

* Portland Maps Permits -- Identify trends in ADU development

### Tech Stack ###

* Django

* PostGIS

* AWS S3

* Heroku//Flask -- potentially service the analytcis modules as individual APIs

* PyData Ecosystem -- analysis

