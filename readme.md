# Create table to store stories before providing as prompt to the model
```
create table stories (
        ID int not null auto_increment, 
        title varchar(128), 
        body text, 
        link varchar(256), 
        sm_api_content text, 
        sm_api_character_count int, 
        sm_api_content_reduced int, 
        sm_api_title varchar(128), 
        primary key (ID)
    );
```
# Insert row
```
insert into stories (link, sm_api_content, sm_api_character_count, sm_api_content_reduced, sm_api_title) values ('https://patch.com/arizona/tucson/pima-county-deliver-pfizer-vaccine-children-12-older', 'PIMA COUNTY, May 12, 2021 - Pima County and its community partners will be offering expanded opportunities to be vaccinated now that the Food and Drug Administration and the Centers for Disease Control and Prevention have endorsed the Emergency Use Authorization of the Pfizer vaccine to include children ages 12 to 15.[BREAK] \"The announcement earlier today is a welcome step in our ongoing battle against COVID-19,\" said Dr. Theresa Cullen, Pima County Health Department director.[BREAK] \"We have been watching and worrying about young people and the variants of COVID-19 for a few weeks. This is an extra and excellent layer of protection to keep them and their loved ones safe.\"[BREAK] The Moderna and Janssen vaccines are only approved for those 18 and older.[BREAK] Pfizer is available at the University of Arizona location, run by the Arizona Department of Health Services, as well as at Tucson Medical Center\'s vaccination site at Morris K. Udall Park, and selected pharmacies.[BREAK] A parent/guardian must be present to consent for their minor child to get a vaccine.[BREAK] The UA location is open until 5 p.m. daily and accepts walk-ups, although registration ahead of time is encouraged at https://www.[BREAK] To find
a pharmacy near you offering the Pfizer vaccine, visit VaccineFinder.org.[BREAK] TMC\'s Udall Park location is open from 8 a.m. - 5 p.m. on weekdays.[BREAK] Tmcaz.com will open Wednesday, May 12, at 6 p.m. for appointments starting this Thursday morning.[BREAK] The Health Department is piloting a mobile clinic with Pfizer this Thursday, May 13, at Canyon del Oro High School from 4:30 p.m. to 7:30 p.m. Please do not arrive before 4 p.m. Walk-ups only, no registration.[BREAK] Pima County expects to make Pfizer available on more dates and locations.[BREAK] Due to increasing heat, the Banner drive-thru vaccination location at Kino Stadium shuttered operations on Monday, May 10.[BREAK] Now serving the area is an indoor location at Kino Event Center, across Ajo Way, which does not have Pfizer vaccine but welcomes anyone age 18 and over for walk-up vaccination.[BREAK] This press release was produced by Pima County Health Department.[BREAK]', 2245, 6, 'Pima
County To Deliver Pfizer Vaccine For Children 12 And Older');
```

# Create table for token information
```create table tokens (prompt_length int, output_length int);```