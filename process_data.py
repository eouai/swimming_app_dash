# import raw CSV, process the file, write to new CSV

import pandas as pd
import re
import numpy as np
import os

#os.chdir('/var/www/FlaskApp/FlaskApp')

year_mapping = {'09':'FR', '10':'SO', '11':'JR', '12':'SR'}
gender_mapping = {'Boys': 'M', 'Men': 'M', 'Girls':'W', 'Women': 'W'}
high_school_mapping = {"AHS": "Alta High School",
                       "Ahs": "Alta High School",
                        "Ahs UT": "Alta High School",
                        "Alta": "Alta High School",
                        "Alta Hawks High School": "Alta High School",
                        "Alta High School ": "Alta High School",
                        "Alta High School A": "Alta High School",
                        "Alta High School-UT": "Alta High School",
                        "Alta High School-UT A": "Alta High School",
                        "Afhs": "American Fork High School",
                        "Afhs-UT": "American Fork High School",
                        "Am. Fork": "American Fork High School",
                        "American Fork": "American Fork High School",
                        "American Fork High Schoo": "American Fork High School",
                        "American Fork High Schoo A": "American Fork High School",
                        "American Fork High School ": "American Fork High School",
                        "American Fork High School A": "American Fork High School",
                        "American Fork High School-UT": "American Fork High School",
                        "American Fork High School-UT A": "American Fork High School",
                        "American Leadership Acad": "American Leadership Academy",
                        "American Leadership Academy A": "American Leadership Academy",
                        "Bear River": "Bear River High School",
                        "Bear River Bears": "Bear River High School",
                        "Bear River High School": "Bear River High School",
                        "Bear River High School ": "Bear River High School",
                        "Bear River High School A": "Bear River High School",
                        "Bear River High School-VA": "Bear River High School",
                        "Bear River High School-VA A": "Bear River High School",
                        "Ben Lomond": "Ben Lomond High School",
                        "Ben Lomond High": "Ben Lomond High School",
                        "Ben Lomond High A": "Ben Lomond High School",
                        "Ben Lomond High School": "Ben Lomond High School",
                        "Ben Lomond High School ": "Ben Lomond High School",
                        "Ben Lomond High School A": "Ben Lomond High School",
                        "Ben Lomond-VA": "Ben Lomond High School",
                        "Ben Lomond-VA A": "Ben Lomond High School",
                        "Blhs": "Ben Lomond High School",
                        "Scots": "Ben Lomond High School",
                        "Bingham": "Bingham High School",
                        "Bingham High School": "Bingham High School",
                        "Bingham High School ": "Bingham High School",
                        "Bingham High School A": "Bingham High School",
                        "Bingham High School-UT": "Bingham High School",
                        "Bingham High School-UT A": "Bingham High School",
                        "Bingham Miners": "Bingham High School",
                        "Bingham Miners A": "Bingham High School",
                        "Bingham-UT": "Bingham High School",
                        "Miners": "Bingham High School",
                        "BONN": "Bonneville High School",
                        "Bonneville": "Bonneville High School",
                        "Bonneville High School": "Bonneville High School",
                        "Bonneville High School ": "Bonneville High School",
                        "Bnftl": "Bountiful High School",
                        "BNTFL": "Bountiful High School",
                        "BNTFL-AK": "Bountiful High School",
                        "Bountiful": "Bountiful High School",
                        "Bountiful High School": "Bountiful High School",
                        "Bountiful High School ": "Bountiful High School",
                        "Bountiful High School A": "Bountiful High School",
                        "Bountiful-UT": "Bountiful High School",
                        "Braves": "Bountiful High School",
                        "BE": "Box Elder High School",
                        "BEHS": "Box Elder High School",
                        "Box Elder": "Box Elder High School",
                        "Box Elder High School": "Box Elder High School",
                        "Box Elder High School ": "Box Elder High School",
                        "Box Elder High School A": "Box Elder High School",
                        "Box Elder-AK": "Box Elder High School",
                        "Box Elder-UT": "Box Elder High School",
                        "A FR Brighton High School": "Brighton High School",
                        "A SO Brighton High School": "Brighton High School",
                        "Bengals": "Brighton High School",
                        "Bengals-UT": "Brighton High School",
                        "Brighton": "Brighton High School",
                        "Brighton High School": "Brighton High School",
                        "Brighton High School ": "Brighton High School",
                        "Brighton High School A": "Brighton High School",
                        "Brighton High School-UT": "Brighton High School",
                        "Brighton High School-UT A": "Brighton High School",
                        "Canyon View": "Canyon View High School",
                        "Canyon View High": "Canyon View High School",
                        "Canyon View High A": "Canyon View High School",
                        "Canyon View High School": "Canyon View High School",
                        "Canyon View High School ": "Canyon View High School",
                        "Canyon View High School A": "Canyon View High School",
                        "Canyonview": "Canyon View High School",
                        "Canyonview High School": "Canyon View High School",
                        "Canyonview High School A": "Canyon View High School",
                        "Canyonview High School-VA": "Canyon View High School",
                        "Canyonview High School-VA A": "Canyon View High School",
                        "Cvhs": "Canyon View High School",
                        "D Canyon View High": "Canyon View High School",
                        "J Canyon View High": "Canyon View High School",
                        "M Canyon View High": "Canyon View High School",
                        "S Canyon View High": "Canyon View High School",
                        "T Canyon View High": "Canyon View High School",
                        "Carbon": "Carbon High School",
                        "Carbon High School": "Carbon High School",
                        "Carbon High School A": "Carbon High School",
                        "Carbon High School-VA": "Carbon High School",
                        "Carbon High School-VA A": "Carbon High School",
                        "Dinos": "Carbon High School",
                        "Cedar City": "Cedar City High School",
                        "Cedar City High": "Cedar City High School",
                        "Cedar City High A": "Cedar City High School",
                        "Cedar City High School": "Cedar City High School",
                        "Cedar City High School ": "Cedar City High School",
                        "Cedar City High School A": "Cedar City High School",
                        "Cedar City High School-VA": "Cedar City High School",
                        "Cedar City High School-VA A": "Cedar City High School",
                        "CedarCity": "Cedar City High School",
                        "Redmen": "Cedar City High School",
                        "Clearfield High School": "Clearfield High School",
                        "Clearfield High School ": "Clearfield High School",
                        "Clear-UT": "Clearfield High School",
                        "Falcons": "Clearfield High School",
                        "Falcons-UT": "Clearfield High School",
                        "Chhs": "Copper Hills High School",
                        "Chhs-UT": "Copper Hills High School",
                        "Copper Hills": "Copper Hills High School",
                        "Copper Hills High School": "Copper Hills High School",
                        "Copper Hills High School ": "Copper Hills High School",
                        "Copper Hills High School A": "Copper Hills High School",
                        "Copper Hills High School-UT": "Copper Hills High School",
                        "Copper Hills High School-UT A": "Copper Hills High School",
                        "Corner Canyon High S": "Corner Canyon High School",
                        "Corner Canyon High S A": "Corner Canyon High School",
                        "Corner Canyon High School": "Corner Canyon High School",
                        "Corner Canyon High School ": "Corner Canyon High School",
                        "COLTS": "Cottonwood High School",
                        "Colts": "Cottonwood High School",
                        "Colts-UT": "Cottonwood High School",
                        "Cottonwood": "Cottonwood High School",
                        "Cottonwood High School": "Cottonwood High School",
                        "Cottonwood High School ": "Cottonwood High School",
                        "Cottonwood High School A": "Cottonwood High School",
                        "Cottonwood High School-UT": "Cottonwood High School",
                        "Cottonwood High School-UT A": "Cottonwood High School",
                        "Cottonwood-UT": "Cottonwood High School",
                        "CYP": "Cyprus High School",
                        "Cyp": "Cyprus High School",
                        "Cyprus": "Cyprus High School",
                        "Cyprus High School": "Cyprus High School",
                        "Cyprus High School ": "Cyprus High School",
                        "Cyprus High School A": "Cyprus High School",
                        "Cyprus-UT": "Cyprus High School",
                        "Davis": "Davis High School",
                        "Davis High School": "Davis High School",
                        "Davis High School ": "Davis High School",
                        "Davis High School A": "Davis High School",
                        "Davis High School-UT": "Davis High School",
                        "Davis High School-UT A": "Davis High School",
                        "Delta": "Delta High School",
                        "Delta High School": "Delta High School",
                        "Delta High School A": "Delta High School",
                        "Delta High School-VA": "Delta High School",
                        "Delta High School-VA A": "Delta High School",
                        "Rabbits": "Delta High School",
                        "Desert Hills": "Desert Hills High School",
                        "Desert Hills High School": "Desert Hills High School",
                        "Desert Hills High School ": "Desert Hills High School",
                        "Desert Hills High School A": "Desert Hills High School",
                        "Desert Hills High School-VA": "Desert Hills High School",
                        "Desert Hills High School-VA A": "Desert Hills High School",
                        "Dhs-UT": "Desert Hills High School",
                        "Dixie": "Dixie High School",
                        "Dixie Flyers": "Dixie High School",
                        "Dixie High School": "Dixie High School",
                        "Dixie High School ": "Dixie High School",
                        "Dixie High School A": "Dixie High School",
                        "Dixie-AK": "Dixie High School",
                        "Dixie-UT": "Dixie High School",
                        "EAST": "East High School",
                        "East": "East High School",
                        "East High School": "East High School",
                        "East High School ": "East High School",
                        "East High School A": "East High School",
                        "East High School Leopards": "East High School",
                        "East High School Leopards A": "East High School",
                        "East-AK": "East High School",
                        "East-UT": "East High School",
                        "Emery": "Emery High School",
                        "Emery High School": "Emery High School",
                        "Emery High School A": "Emery High School",
                        "Emery High School-UT": "Emery High School",
                        "Emery High School-UT A": "Emery High School",
                        "FHS-UT": "Fremont High School",
                        "Fremont": "Fremont High School",
                        "Fremont High School": "Fremont High School",
                        "Fremont High School ": "Fremont High School",
                        "Fremont High School A": "Fremont High School",
                        "Fremont High School-UT": "Fremont High School",
                        "Fremont High School-UT A": "Fremont High School",
                        "Ghs Swimming-VA": "Gainesville High School",
                        "Grand County High Schoo": "Grand County High School",
                        "Grand County High Schoo A": "Grand County High School",
                        "Grand County High School": "Grand County High School",
                        "Granger High School": "Granger High School",
                        "Granger High School ": "Granger High School",
                        "Ghs": "Grantsville High School",
                        "Ghs Swimming-VA A": "Grantsville High School",
                        "Grantsville": "Grantsville High School",
                        "Grantsville High School": "Grantsville High School",
                        "Grantsville High School A": "Grantsville High School",
                        "Green Canyon High School": "Green Canyon High School",
                        "Green Canyon High School ": "Green Canyon High School",
                        "Gunnison Valley High Scho": "Gunnison Valley High School",
                        "Gunnison Valley High School": "Gunnison Valley High School",
                        "Herriman High School": "Herriman High School",
                        "Herriman High School ": "Herriman High School",
                        "Herriman High School A": "Herriman High School",
                        "HIGH": "Highland High School",
                        "Highland": "Highland High School",
                        "Highland High School": "Highland High School",
                        "Highland High School ": "Highland High School",
                        "Highland High School A": "Highland High School",
                        "Highland-AK": "Highland High School",
                        "Highland-UT": "Highland High School",
                        "Hillcrest": "Hillcrest High School",
                        "Hillcrest High High School": "Hillcrest High School",
                        "Hillcrest High High School A": "Hillcrest High School",
                        "Hillcrest High School": "Hillcrest High School",
                        "Hillcrest High School ": "Hillcrest High School",
                        "Hillcrest High School A": "Hillcrest High School",
                        "HILL-UT": "Hillcrest High School",
                        "Huskies": "Hillcrest High School",
                        "Hunter": "Hunter High School",
                        "Hunter High School": "Hunter High School",
                        "Hunter High School ": "Hunter High School",
                        "Hunter High School A": "Hunter High School",
                        "Hunter High School-UT": "Hunter High School",
                        "Hunter High School-UT A": "Hunter High School",
                        "Wolverines": "Hunter High School",
                        "Wolverines-UT": "Hunter High School",
                        "Hurricane": "Hurricane High School",
                        "Hurricane High School": "Hurricane High School",
                        "Hurricane High School ": "Hurricane High School",
                        "Hurricane High School A": "Hurricane High School",
                        "Hurricane High School-VA": "Hurricane High School",
                        "Hurricane High School-VA A": "Hurricane High School",
                        "Ics": "Intermountain Christian School",
                        "ICS": "Intermountain Christian School",
                        "Inter Mtn": "Intermountain Christian School",
                        "Intermountain Christian High": "Intermountain Christian School",
                        "Intermountain Christian School": "Intermountain Christian School",
                        "Intermountain Christian School-VA": "Intermountain Christian School",
                        "Intermountian": "Intermountain Christian School",
                        "JOR": "Jordan High School",
                        "Jordan": "Jordan High School",
                        "Jordan High School": "Jordan High School",
                        "Jordan High School ": "Jordan High School",
                        "Jordan High School A": "Jordan High School",
                        "Jordan High School-UT": "Jordan High School",
                        "FR Juan Diego High School": "Juan Diego Catholic High School",
                        "Jdchs": "Juan Diego Catholic High School",
                        "Juan Deigo": "Juan Diego Catholic High School",
                        "Juan Diego": "Juan Diego Catholic High School",
                        "Juan Diego Catholic High Schoo": "Juan Diego Catholic High School",
                        "Juan Diego Catholic High Schoo A": "Juan Diego Catholic High School",
                        "Juan Diego Catholic High School": "Juan Diego Catholic High School",
                        "Juan Diego Catholic High Schoo-UT": "Juan Diego Catholic High School",
                        "Juan Diego Catholic High Schoo-UT A": "Juan Diego Catholic High School",
                        "Juan Diego High Schoo": "Juan Diego Catholic High School",
                        "Juan Diego High Schoo A": "Juan Diego Catholic High School",
                        "Juan Diego High School": "Juan Diego Catholic High School",
                        "JUDG": "Judge Memorial High School",
                        "Judge": "Judge Memorial High School",
                        "Judge Memorial": "Judge Memorial High School",
                        "Judge Memorial Catholic High S": "Judge Memorial High School",
                        "Judge Memorial Catholic High S A": "Judge Memorial High School",
                        "Judge Memorial Catholic High S-UT": "Judge Memorial High School",
                        "Judge Memorial Catholic High S-UT A": "Judge Memorial High School",
                        "Judge Memorial High School": "Judge Memorial High School",
                        "Judge Memorial High School A": "Judge Memorial High School",
                        "Kearns": "Kearns High School",
                        "Kearns Cougars": "Kearns High School",
                        "Kearns Cougars-UT": "Kearns High School",
                        "Kearns High School": "Kearns High School",
                        "Kearns High School ": "Kearns High School",
                        "Kearns High School A": "Kearns High School",
                        "Kearns High School-UT": "Kearns High School",
                        "Kearns High School-UT A": "Kearns High School",
                        "LAYTN": "Layton High School",
                        "LAYTN-UT": "Layton High School",
                        "Layton": "Layton High School",
                        "Layton High School": "Layton High School",
                        "Layton High School ": "Layton High School",
                        "Layton High School A": "Layton High School",
                        "Layton High School-UT": "Layton High School",
                        "LEHI": "Lehi High School",
                        "Lehi": "Lehi High School",
                        "Lehi High School": "Lehi High School",
                        "Lehi High School ": "Lehi High School",
                        "Lehi High School A": "Lehi High School",
                        "Lehi High School-UT": "Lehi High School",
                        "Lehi High School-UT A": "Lehi High School",
                        "Lehi-AK": "Lehi High School",
                        "Logan": "Logan High School",
                        "Logan High School": "Logan High School",
                        "Logan High School ": "Logan High School",
                        "Logan High School A": "Logan High School",
                        "Logan-AK": "Logan High School",
                        "SR Logan High School": "Logan High School",
                        "Knights-UT": "Lone Peak High School",
                        "Lone Peak": "Lone Peak High School",
                        "Lone Peak High School": "Lone Peak High School",
                        "Lone Peak High School ": "Lone Peak High School",
                        "Lone Peak High School A": "Lone Peak High School",
                        "Lone Peak High School-UT": "Lone Peak High School",
                        "Lone Peak High School-UT A": "Lone Peak High School",
                        "Lone Peak-UT": "Lone Peak High School",
                        "Lphs": "Lone Peak High School",
                        "Maeser Prep High School": "Maeser Prep High School",
                        "Maeser Prep High Shcool": "Maeser Prep High School",
                        "Maple Mountain High School": "Maple Mountain High School",
                        "Maple Mountain High School ": "Maple Mountain High School",
                        "Maple Mountain High School A": "Maple Mountain High School",
                        "Maple Mountain-AK": "Maple Mountain High School",
                        "MHS": "Millard High School",
                        "Millard High School": "Millard High School",
                        "Morgan High High School": "Morgan High School",
                        "MCHS": "Mountain Crest High School",
                        "Mountain Crest": "Mountain Crest High School",
                        "Mountain Crest High School": "Mountain Crest High School",
                        "Mountain Crest High School ": "Mountain Crest High School",
                        "Mountain Crest High School A": "Mountain Crest High School",
                        "Mountain Crest-UT": "Mountain Crest High School",
                        "Mt Crest-AK": "Mountain Crest High School",
                        "Mountain View": "Mountain View High School",
                        "Mountain View High School": "Mountain View High School",
                        "Mountain View High School ": "Mountain View High School",
                        "Mountain View High School A": "Mountain View High School",
                        "Mountain View-UT": "Mountain View High School",
                        "Mt View-AK": "Mountain View High School",
                        "Mtn View": "Mountain View High School",
                        "Mvhs": "Mountain View High School",
                        "Murray": "Murray High School",
                        "Murray High School": "Murray High School",
                        "Murray High School ": "Murray High School",
                        "Murray High School A": "Murray High School",
                        "Murray-UT": "Murray High School",
                        "Spartans": "Murray High School",
                        "North Sanpete High School": "North Sanpete High School",
                        "NSHS": "North Sanpete High School",
                        "North Summit": "North Summit High",
                        "North Summit High": "North Summit High",
                        "North Summit High Schoo": "North Summit High",
                        "North Summit High School": "North Summit High",
                        "North Summit High School A": "North Summit High",
                        "North Summit HS": "North Summit High",
                        "North Summit HS A": "North Summit High",
                        "North Summit-VA": "North Summit High",
                        "North Summit-VA A": "North Summit High",
                        "NORTH": "Northridge High School",
                        "Northridge": "Northridge High School",
                        "Northridge High School": "Northridge High School",
                        "Northridge High School ": "Northridge High School",
                        "Northridge High School A": "Northridge High School",
                        "Northridge High School-UT": "Northridge High School",
                        "OAKL": "Oakley High School",
                        "Oakley": "Oakley High School",
                        "Oakley High School": "Oakley High School",
                        "Oakley High School A": "Oakley High School",
                        "Oakley School": "Oakley High School",
                        "Oakley School A": "Oakley High School",
                        "Ogden": "Ogden High School",
                        "Ogden High School": "Ogden High School",
                        "Ogden High School A": "Ogden High School",
                        "Ogden High Swimming": "Ogden High School",
                        "Ogden High Swimming ": "Ogden High School",
                        "Ogden-AK": "Ogden High School",
                        "Ohs Tigers": "Ogden High School",
                        "Tigers": "Ogden High School",
                        "OLY": "Olympus High School",
                        "Oly": "Olympus High School",
                        "Olympus": "Olympus High School",
                        "Olympus High School": "Olympus High School",
                        "Olympus High School ": "Olympus High School",
                        "Olympus High School A": "Olympus High School",
                        "Olympus-AK": "Olympus High School",
                        "Olympus-UT": "Olympus High School",
                        "Orem": "Orem High School",
                        "OREM": "Orem High School",
                        "Orem High School": "Orem High School",
                        "Orem High School ": "Orem High School",
                        "Orem High School A": "Orem High School",
                        "Orem High School Tigers": "Orem High School",
                        "Orem High School Tigers A": "Orem High School",
                        "Orem-AK": "Orem High School",
                        "Orem-UT": "Orem High School",
                        "Park": "Park City High School",
                        "Park City": "Park City High School",
                        "Park City High School": "Park City High School",
                        "Park City High School ": "Park City High School",
                        "Park City High School A": "Park City High School",
                        "Park City High School-VA": "Park City High School",
                        "Park City High School-VA A": "Park City High School",
                        "ParkCity": "Park City High School",
                        "Parowan": "Parowan High School",
                        "Payson High School": "Payson High School",
                        "Payson High School ": "Payson High School",
                        "Payson High School A": "Payson High School",
                        "Pineview": "Pine View High School",
                        "Pine View": "Pine View High School",
                        "Pine View High Schoool": "Pine View High School",
                        "Pine View-UT": "Pine View High School",
                        "PineView": "Pine View High School",
                        "PineView High School": "Pine View High School",
                        "PineView High School ": "Pine View High School",
                        "PineView High School A": "Pine View High School",
                        "PineView-AK": "Pine View High School",
                        "Pghs": "Pleasant Grove High School",
                        "Pleasant Grove": "Pleasant Grove High School",
                        "Pleasant Grove High School": "Pleasant Grove High School",
                        "Pleasant Grove High School ": "Pleasant Grove High School",
                        "Pleasant Grove High School A": "Pleasant Grove High School",
                        "Pleasant Grove High School-UT": "Pleasant Grove High School",
                        "Pleasant Grove High School-UT A": "Pleasant Grove High School",
                        "PROVO": "Provo High School",
                        "Provo": "Provo High School",
                        "Provo High School": "Provo High School",
                        "Provo High School ": "Provo High School",
                        "Provo High School A": "Provo High School",
                        "PROVO-AK": "Provo High School",
                        "Provo-UT": "Provo High School",
                        "Richfield": "Richfield High School",
                        "Richfield High School": "Richfield High School",
                        "Richfield High School A": "Richfield High School",
                        "Richfield High School Wildcats-VA": "Richfield High School",
                        "Richfield High School Wildcats-VA A": "Richfield High School",
                        "Wildcats": "Richfield High School",
                        "Ridgeline High School": "Ridgeline High School",
                        "Ridgeline High School ": "Ridgeline High School",
                        "Riverton": "Riverton High School",
                        "Riverton High School": "Riverton High School",
                        "Riverton High School ": "Riverton High School",
                        "Riverton High School A": "Riverton High School",
                        "Riverton High School-UT": "Riverton High School",
                        "Riverton High School-UT A": "Riverton High School",
                        "RHSM": "Rowland Hall High School",
                        "RH": "Rowland Hall High School",
                        "Rhsm": "Rowland Hall High School",
                        "Rowland Hall": "Rowland Hall High School",
                        "Rowland Hall High School": "Rowland Hall High School",
                        "Rowland Hall High School A": "Rowland Hall High School",
                        "Rowland Hall HS": "Rowland Hall High School",
                        "Rowland Hall HS A": "Rowland Hall High School",
                        "Rowland Hall St. Marks": "Rowland Hall High School",
                        "Rowland Hall St. Marks A": "Rowland Hall High School",
                        "Rowland Hall St. Marks-VA": "Rowland Hall High School",
                        "Rowland Hall St. Marks-VA A": "Rowland Hall High School",
                        "RHS": "Roy High School",
                        "Roy": "Roy High School",
                        "Roy High School": "Roy High School",
                        "Roy High School ": "Roy High School",
                        "Roy High School A": "Roy High School",
                        "Royals": "Roy High School",
                        "Roy-UT": "Roy High School",
                        "Saint Joseph High School": "Saint Joseph High School",
                        "Salem Hills": "Salem Hills High School",
                        "Salem Hills High School": "Salem Hills High School",
                        "Salem Hills High School ": "Salem Hills High School",
                        "Salem Hills High School A": "Salem Hills High School",
                        "Salt Lake Lutheran High School-VA": "Salt Lake Lutheran High School",
                        "Sky View": "Sky View High School",
                        "Sky View High School": "Sky View High School",
                        "Sky View High School ": "Sky View High School",
                        "Sky View High School A": "Sky View High School",
                        "Sky View-AK": "Sky View High School",
                        "Sky View-UT": "Sky View High School",
                        "SV": "Sky View High School",
                        "SVHS": "Sky View High School",
                        "R JR Skyline High School": "Skyline High School",
                        "R SO Skyline High School": "Skyline High School",
                        "R SR Skyline High School": "Skyline High School",
                        "Skyline": "Skyline High School",
                        "Skyline High School": "Skyline High School",
                        "Skyline High School A": "Skyline High School",
                        "Skyline Swim Team": "Skyline High School",
                        "Skyridge High School": "Skyline High School",
                        "Skyridge High School ": "Skyline High School",
                        "SKY-UT": "Skyline High School",
                        "Snow Canyon": "Snow Canyon High School",
                        "Snow Canyon High School": "Snow Canyon High School",
                        "Snow Canyon High School ": "Snow Canyon High School",
                        "Snow Canyon High School A": "Snow Canyon High School",
                        "Snow Canyon-AK": "Snow Canyon High School",
                        "Snow Canyon-UT": "Snow Canyon High School",
                        "South Sevier High School": "South Sevier High School",
                        "South Summit": "South Summit High School",
                        "South Summit High School": "South Summit High School",
                        "South Summit High School Swim": "South Summit High School",
                        "South Summit High School Swim A": "South Summit High School",
                        "SSHS": "South Summit High School",
                        "Sfhs": "Spanish Fork High School",
                        "Spanish Fork": "Spanish Fork High School",
                        "Spanish Fork High": "Spanish Fork High School",
                        "Spanish Fork High A": "Spanish Fork High School",
                        "Spanish Fork High School": "Spanish Fork High School",
                        "Spanish Fork High School ": "Spanish Fork High School",
                        "Spanish Fork High School A": "Spanish Fork High School",
                        "Spanish Fork-AK": "Spanish Fork High School",
                        "SpanishFork": "Spanish Fork High School",
                        "Red Devlis": "Springville High School",
                        "Springville": "Springville High School",
                        "Springville High School": "Springville High School",
                        "Springville High School ": "Springville High School",
                        "Springville High School A": "Springville High School",
                        "Springville-AK": "Springville High School",
                        "Springville-UT": "Springville High School",
                        "SPRV": "Springville High School",
                        "Stanbury High School": "Stansbury High School",
                        "Stanbury High School A": "Stansbury High School",
                        "Stansbury High School": "Stansbury High School",
                        "Stansbury High School ": "Stansbury High School",
                        "Stansbury High School A": "Stansbury High School",
                        "Stansbury-AK": "Stansbury High School",
                        "Summit Academy High School": "Summit Academy High School",
                        "Summit Academy High School A": "Summit Academy High School",
                        "Syr": "Syracuse High School",
                        "Syracuse": "Syracuse High School",
                        "Syracuse High School": "Syracuse High School",
                        "Syracuse High School ": "Syracuse High School",
                        "Syracuse High School Swimiming": "Syracuse High School",
                        "Syracuse High School-UT": "Syracuse High School",
                        "Syracuse High School-UT A": "Syracuse High School",
                        "Tayl": "Taylorsville High School",
                        "Taylorsville": "Taylorsville High School",
                        "Taylorsville High School": "Taylorsville High School",
                        "Taylorsville High School ": "Taylorsville High School",
                        "Taylorsville High School A": "Taylorsville High School",
                        "Taylorsville High School-UT": "Taylorsville High School",
                        "Taylorsville High School-UT A": "Taylorsville High School",
                        "THS": "Taylorsville High School",
                        "Ths": "Taylorsville High School",
                        "T-Ville": "Taylorsville High School",
                        "Telos Academy": "Telos Academy High School",
                        "Telos Academy High School": "Telos Academy High School",
                        "Timpanogos High Schol": "Timpanogos High School",
                        "Timpanogos High Schol A": "Timpanogos High School",
                        "Timp": "Timpview High School",
                        "TIMP": "Timpview High School",
                        "Timpview": "Timpview High School",
                        "Timpview High School": "Timpview High School",
                        "Timpview High School ": "Timpview High School",
                        "Timpview High School A": "Timpview High School",
                        "Timpview-AK": "Timpview High School",
                        "Timpview-UT": "Timpview High School",
                        "Tooele": "Tooele High School",
                        "Tooele High School": "Tooele High School",
                        "Tooele High School ": "Tooele High School",
                        "Tooele High School A": "Tooele High School",
                        "Tooele-AK": "Tooele High School",
                        "Tooele-UT": "Tooele High School",
                        "Uintah": "Uintah High School",
                        "Uintah High School": "Uintah High School",
                        "Uintah High School ": "Uintah High School",
                        "Uintah High School A": "Uintah High School",
                        "Uintah High School Swim Team": "Uintah High School",
                        "Uintah High School Swim Team A": "Uintah High School",
                        "Uintah-AK": "Uintah High School",
                        "Utes": "Uintah High School",
                        "Union High School": "Union High School",
                        "VHS": "Viewmont High School",
                        "Vhs": "Viewmont High School",
                        "Viewmont": "Viewmont High School",
                        "Viewmont High School": "Viewmont High School",
                        "Viewmont High School ": "Viewmont High School",
                        "Viewmont High School A": "Viewmont High School",
                        "Viewmont HighSchool-UT": "Viewmont High School",
                        "Viewmont HighSchool-UT A": "Viewmont High School",
                        "Vikings": "Viewmont High School",
                        "Vikings-UT": "Viewmont High School",
                        "Wasatch Academy High Sch": "Wasatch Academy High School",
                        "Wasatch Academy High School": "Wasatch Academy High School",
                        "Wasatch Academy Swim Team": "Wasatch Academy High School",
                        "WASA": "Wasatch High School",
                        "Wasatch": "Wasatch High School",
                        "Wasatch High School": "Wasatch High School",
                        "Wasatch High School ": "Wasatch High School",
                        "Wasatch High School A": "Wasatch High School",
                        "Wasatch High School-VA": "Wasatch High School",
                        "Wasatch High School-VA A": "Wasatch High School",
                        "Waterford": "Waterford High School",
                        "Waterford High School": "Waterford High School",
                        "Waterford High School A": "Waterford High School",
                        "Waterford High School-VA": "Waterford High School",
                        "WTFD": "Waterford High School",
                        "Weber": "Weber High School",
                        "Weber High School": "Weber High School",
                        "Weber High School ": "Weber High School",
                        "Weber High School A": "Weber High School",
                        "Weber High School-UT": "Weber High School",
                        "Weber High School-UT A": "Weber High School",
                        "WEST": "West High School",
                        "West": "West High School",
                        "West High School": "West High School",
                        "West High School ": "West High School",
                        "West High School A": "West High School",
                        "West High School-UT": "West High School",
                        "West High School-UT A": "West High School",
                        "West-UT": "West High School",
                        "West Jordan": "West Jordan High School",
                        "West Jordan High School": "West Jordan High School",
                        "West Jordan High School A": "West Jordan High School",
                        "West Jordan High School-UT": "West Jordan High School",
                        "West Jordan High School-UT A": "West Jordan High School",
                        "WJ": "West Jordan High School",
                        "WJ-UT": "West Jordan High School",
                        "West Lake-AK": "Westlake High School",
                        "Westlake High School": "Westlake High School",
                        "Westlake High School ": "Westlake High School",
                        "Westlake High School A": "Westlake High School",
                        "R SR Woods Cross High School": "Woods Cross High School",
                        "Woods Cross": "Woods Cross High School",
                        "Woods Cross High School": "Woods Cross High School",
                        "Woods Cross High School ": "Woods Cross High School",
                        "Woods Cross High School A": "Woods Cross High School",
                        "Woods Cross-AK": "Woods Cross High School",
                        "Woods Cross-UT": "Woods Cross High School",
                        "Wxhs": "Woods Cross High School",
                        "WXHS": "Woods Cross High School",
                       }


# Read in initial data sets from CSV.
df_SV_raw = pd.read_csv('data/swimming_data.csv')
df_state_raw = pd.read_csv('data/swimming_data_state.csv')
df_state_raw = df_state_raw[np.isfinite(df_state_raw['key'])]


# Define CSV cleanup and processing methods
def cleanup_SV(df):
    df['Year'] = pd.DatetimeIndex(df['Date']).year
    df = df[['Event', 'Time Full', 'Year', 'Swimmer', 'Gender']]
    return df


def cleanup_state(df):
    df = process_place(df)
    df = process_school_year(df)
    df = process_gender(df)
    df = reshape_seed(df)
    df = process_times(df)
    df = process_school_name(df)
    return df


def process_school_name(df):
    df['School'] = df['School'].apply(lambda x: x.strip())
    df['School'] = df['School'].apply(
        lambda x: high_school_mapping[x] if x in high_school_mapping else x)
    return df


def process_place(df):
    # Fill NA with 0 and convert col to int format
    df['Place'] = df['Place'].fillna(0)
    df['Place'] = df['Place'].apply(lambda x: int(x))
    return df


def process_school_year(df):
    # Standardize school year formatting
    # Remove school year when it appears in school name col 'School'
    df['Year'] = df['Year'].fillna('NA')
    df['Year'] = df['Year'].apply(lambda x: '09' if x == '9' else x)
    school_years = [' FR ', ' SO ', ' JR ', ' SR ', ' 09 ', ' 10 ', ' 11 ', ' 12 ']
    df['Year'] = df['Year'].apply(
            lambda x: x if any(x == year for year in map(str.strip, school_years)) else 'NA')
    for index, row in df.iterrows():
        if pd.isnull(row['School']):
            continue
        else:
            school_name = row['School']
            for year in school_years:
                if year in school_name:
                    if row['Year'] not in map(str.strip, school_years):
                        df.loc[index, 'Year'] = year.strip()
                    df.loc[index, 'School'] = school_name[school_name.find(year) + 4:]
                    break
    df['Year'].replace(year_mapping, inplace=True)
    return df


def process_gender(df):
    # Standardize gender formatting
    df['Gender'].replace(gender_mapping, inplace=True)
    return df


def sub_chars(x):
    if x is not None:
        if len(re.findall('\d', x)) > 0:
            x = re.sub("[^0-9.:]", "", x)
        else:
            x = ''
    else:
        x = ''
    return x


def reshape_seed(df):
    df['Final Time'] = df['Final Time'].fillna(value='')
    df['Seed'] = df['Seed'].fillna(value='')
    df_temp = df[['key', 'Place', 'Swimmer', 'Year', 'School', 'Gender',
                  'Event', 'Seed', 'Final Time', 'Date', 'Class', 'full_results']]
    df_temp['seed_check'] = df_temp['Seed'].apply(lambda x: len(x))
    df_temp = df_temp[df_temp['seed_check'] > 1]
    df_temp = df_temp.drop(columns='seed_check')
    df['Seed'] = ''
    df_temp['Final Time'] = ''
    df_temp['Meet'] = 'State Seed'
    df_combined = pd.concat([df_temp, df])
    final_times = list(df_combined['Final Time'])
    seed_times = list(df_combined['Seed'])
    count = 0
    swim_times = []
    for item in final_times:
        if len(item) > 0:
            swim_times.append(item)
        else:
            swim_times.append(seed_times[count])
        if len(item) > 1 and len(seed_times[count]) > 1:
            print(item)
            print(seed_times[count])
        count += 1
    df_combined['swim_time'] = swim_times
    df_combined = df_combined.drop(columns=['Seed', 'Final Time'])

    return df_combined


def time_format(time_split):
    try:
        if len(time_split) == 0:
            time_str_format = '2000-01-01 00:59:59.99'
        elif (len(time_split) == 1) & (len(time_split[0]) == 0):
            time_str_format = '2000-01-01 00:59:59.99'
        elif (len(time_split) == 1) & (time_split[0] == ' '):
            time_str_format = '2000-01-01 00:59:59.99'
        elif (len(time_split) == 1) & (len(time_split[0]) > 0):
            time_str_format = '2000-01-01 00:00:' + time_split[0]
        else:
            time_str_format = '2000-01-01 00:' + time_split[0] + ':' + time_split[1]
        time_obj = pd.datetime.strptime(time_str_format, '%Y-%m-%d %H:%M:%S.%f')
    except:
        print(time_split)
    return time_obj


def process_times(df):
    df[['50 Split', '100 Split', '150 Split', '200 Split', '250 Split',
        '300 Split', '350 Split', '400 Split', '450 Split', '500 Split']] = \
        df[['50 Split', '100 Split', '150 Split', '200 Split', '250 Split',
            '300 Split', '350 Split', '400 Split', '450 Split', '500 Split']].fillna(value='')
    df['time_cleanup'] = df['swim_time'].apply(lambda x: sub_chars(x))
    df['time_obj'] = df['time_cleanup'].apply(lambda x: time_format(x.split(":")))
    df['50 Split'] = df['50 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['100 Split'] = df['100 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['150 Split'] = df['150 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['200 Split'] = df['200 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['250 Split'] = df['250 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['300 Split'] = df['300 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['350 Split'] = df['350 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['400 Split'] = df['400 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['450 Split'] = df['450 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['500 Split'] = df['500 Split'].apply(lambda x: time_format(str(x).split(":")))
    df['date_time'] = pd.to_datetime(df['Date'])
    df['date_year'] = df['date_time'].map(lambda x: x.year)
    return df


# Cleanup and process the CSV files
df_SV = cleanup_SV(df_SV_raw)
df_state = cleanup_state(df_state_raw)

df_SV.to_csv('data/swimming_data_processed.csv')
df_state.to_csv('data/swimming_data_state_processed.csv')