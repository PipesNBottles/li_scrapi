"""
MIT License

Copyright (c) 2024 Tom Quirk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from enum import IntEnum, Enum


class Experience(IntEnum):
    INTERN = 1
    ENTRY = 2
    ASSOCIATE = 3
    MID_SENIOR = 4
    DIRECTOR = 5
    EXECUTIVE = 6


class NetworkDepth(Enum):
    FIRST = "F"
    SECOND = "S"
    OTHER = "O"


class JobType(Enum):
    FULL_TIME = "F"
    CONTRACT = "C"
    PART_TIME = "P"
    TEMPORARY = "T"
    INTERN = "I"
    VOLUNTEER = "V"
    OTHER = "O"


class LocationType(IntEnum):
    ONSITE = 1
    REMOTE = 2
    HYBRID = 3


class SortOrder(Enum):
    RELEVANCE = "RELEVANCE"
    LATEST = "REVERSE_CHRONOLOGICAL"


class SortBy(Enum):
    RELEVANCE = "R"
    DATE = "DD"


class CompanyID(IntEnum):
    GOOGLE = 1441
    APPLE = 162479


class JobTitle(IntEnum):
    SOFTWARE_ENGINEER = 9
    CLOUD_ENGINEER = 3006


class GeoID(IntEnum):
    # Countries
    USA = 103644278
    CANADA = 101174742

    # Cities
    ATLANTA = 106224388
    AUSTIN = 104472865
    BALTIMORE = 106330734
    BOSTON = 102380872
    CHARLOTTE = 102264677
    CHICAGO = 103112676
    COLUMBUS = 102812094
    DALLAS = 104194190
    DC = 104383890
    DENVER = 103736294
    DETROIT = 103624908
    FORT_WORTH = 100432370
    HOUSTON = 103743442
    KANSAS_CITY_KANSAS = 104388316
    KANSAS_CITY_MISSOURI = 106142749
    LOS_ANGELES = 102448103
    MIAMI = 102394087
    MINNEAPOLIS = 103039849
    MONTREAL = 101330853
    NEW_YORK = 105080838
    OTTAWA = 106234700
    PHILLY = 104937023
    PHOENIX = 100219842
    PORTLAND = 104727230
    RALEIGH = 100197101
    SALT_LAKE_CITY = 103250458
    SAN_DIEGO = 103918656
    SAN_FRANCISCO = 102277331
    SEATTLE = 104116203
    ST_LOUIS = 104428936
    ST_PAUL = 102370339
    TAMPA = 105517665
    TORONTO = 100025096
    VANCOUVER = 103366113

    # Metros
    ATLANTA_METRO = 90000052
    AUSTIN_METRO = 90000064
    BOSTON_METRO = 90000007
    CHARLOTTE_METRO = 90000152
    CHICAGO_METRO = 90000014
    COLUMBUS_METRO = 90000184
    DALLAS_METRO = 90000031
    DC_METRO = 90000097
    DENVER_METRO = 90000034
    DETROIT_METRO = 90000035
    HOUSTON_METRO = 90000042
    KANSAS_CITY_METRO = 90000376
    LOS_ANGELES_METRO = 90000049
    MIAMI_METRO = 90000056
    MINNEAPOLIS_METRO = 90000512
    MONTREAL_METRO = 90009540
    NEW_YORK_METRO = 90000070
    OTTAWA_METRO = 90009542
    PHILLY_METRO = 90000077
    PHOENIX_METRO = 90000620
    PORTLAND_METRO = 90000079
    RALEIGH_METRO = 90000664
    SALT_LAKE_CITY_METRO = 90000716
    SAN_DIEGO_METRO = 90010472
    SAN_FRANCISCO_METRO = 90000084
    SEATTLE_METRO = 90000091
    ST_LOUIS_METRO = 90000704
    TAMPA_METRO = 90000828
    TORONTO_METRO = 90009551
    VANCOUVER_METRO = 90009553
