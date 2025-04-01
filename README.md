# oneFMS API
Fleet Management Services API tests
* API Endpoints to be tested

## Prerequisites
```
Pycharm - Community Edition
python3.10 and above
```

**oneFMS Swagger API:**
```
* URL : https://api-onefms-uat.zig.live/swagger-ui/index.html#/
```

**Quick Start (follow the steps to run tests and see results)**
```
1.	Get latest python3.10 and above with pip installed [**must]
2.	Clone git folder **‘oneFMS.git’** or download ***'oneFMS-main'*** to local machine
3.	Root folder is **‘oneFMS>’ – All project files/folders parked here.**
```

##### Folders with files and Others:
```
1. test_data[testcases written with testdata as excel format], 
2. reports[results in form of Html and excel formats], 
3. test_dir[Api test(test_api_fms.py inherit with data driven using files from test_data and py files from utils]
4. utils [validating the request and response of api using the actual and expected results given in testcases]
5. requirements.txt[defining the list of libraries, which needs to be installed, after python installed]
6. run.py [Initial test execution file]
```

###### Project Structure
```
-----------
    ├── fms                                 <- Included all fms api related methods and functions to generate payload to make a request ,..
    │   ├── fmsextract.py                   <- Extraction each individual fms api endpoints.
    │   ├── vehicle_data.py                 <- Auto generation of json response to correlate data to generate payload for dependent api.
    │   ├── vehicle_dict.py                 <- Generation of payload based on api endpoint parameters and correlation data
    ├── reports                             <- Reports and logs are parked here as excel and html format.
    ├── test_data                           <- Folder contains all api testcases with test data.
    │   ├── json_data                       <- Auto generation of json response to correlate and use for dependent cases.
    │   ├── api_test_data.xlsx              <- Use this format to add the testcases and test data for exeution
    ├── test_dir                            <- Main source code folder
    │   ├── test_onefms_api.py              <- Inherit all functions to start execute the tests.
    ├── utils                               <- Included all base actions, commonhelpers,..
    │       ├── api.py                      <- Functions for https methods and generic API payloads                      
    │       ├── apiexecutor.py              <- Functions relate to fms api's to valid for json api response
    │       ├── endpointapi.ini             <- Contains api endpoint headers to used for test
    ├── config.ini                          <- Contains key-value pair for properties and sections for test
    ├── README.md                           <- README for users using this project instructions.
    ├── requirements.txt                    <- Contains mandatory py libraries to be used for this project.
    ├── run.py                              <- Execute this to start the fms api tests.
```

**Once done with above steps then continue in terminal**
```
1.	pip install virtualenv
2.	To isolate virtual environment, Goto **‘oneFMS’> Type Command: ‘python -m venv oneFMSAPI_tests’**
3.	To get isolated environment, Go to folder **‘oneFMSAPI_tests>Scripts’ and Type: ‘activate’**
4.	Go back to root folder **‘fmsAPI’**
5.	To install all necessary packages, need to run the sample tests, Type: **‘pip install -r requirements.txt’**
```

**Run the test and see results**
```
Tagging argument(--t=): [Smoke, Regression, Skip]
1.	Type to run only api tests: **‘oneFMS>python run.py --t=Smoke’**
2.	After Executions, Results displays under reports folder[*.html, *.xlsx]
```


