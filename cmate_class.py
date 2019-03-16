'''
    This is a project that will provide the functionality to test code right in
    your terminal against the sample test cases that are provided in the question

    I solve lot of programming questions and what i have to do is to fetch the test case by 
    copying them and then pasting them. Lot of repetitive task which can be automated 
    using power of languages such as python.

    The basic idea of this project is to fetch the required problem page and parse it 
    to get the required test cases and their output and then test it against the output 
    generated by the code submitted for the problem.

    Enough talking let's start implementing!!

    Currently developing for Codeforces, Codechef
    
    Will extend for :
    Hackerrank
'''

#All the necessary imports
try:
    from bs4 import BeautifulSoup as bs
    import requests
    import os
    import re
    import itertools
    import shutil
except:
    print("Install necessary dependencies and then try again.")
    exit(0)

class SITE:
    """
        Base class to support reusability of modules that work on same functionality.
        Basically implementing abstraction
    """
    def __init__(self):
        pass
    
    def get_page_data(self, problem_code):
        '''
            Description:
                Given the problem code like C this function is responsible 
                for fetching html page from appropriate 
                problem url.
            I/O: 
                problem_code(string)
            O/P:
                html_page_data
        '''
        page_url = self.construct_problem_url(problem_code)
        # print(page_url)
        try:
            for tries in range(self.MAX_TRIES):
                page_data = requests.get(page_url)
                if page_data.status_code == 200:
                    print("Fetched Page to parse test cases")
                    return page_data
        except:
            print("Could not connect to the {} site. Try again later.".format(self.site))
            exit(0)

    @staticmethod
    def clean_structure(dirc):
        if dirc:
            for cur_file in os.listdir(dirc):
                file_path = os.path.join(dirc, cur_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    print("Error: Issues occurred while deleting files. Please try again later.")
        return

#Class Codeforces
class CODEFORCES(SITE):
    '''
    Description:
        This class will contain all the functions
        and properties related to how things need to be done for Codeforces website
    '''
    folder = None
    url = 'https://www.codeforces.com'
    MAX_TRIES = 5
    site = 'Codeforces'
    def __init__(self, contest_code):
        #constructor
        '''
            Description:
                Initialize all the properties of Codeforces Class
        '''
        self.contest_code = contest_code
        #   Check whether necessary folder structure is in place or not
        #   So that the test files could be saved there
        self.cp_dir = (os.path.join(CODEFORCES.folder, self.contest_code))
        if(not os.path.exists(self.cp_dir)):
            os.makedirs(self.cp_dir)


    def construct_problem_url(self, problem_code):
        '''
            Description:
                Given the problem code like 1111C which means problem C from contest 1111
                this function is responsible for constructing the appropriate problem url.
            I/O: 
                problem_code(string)
            O/P:
                url(string)
        '''
        if problem_code:
            return self.url + '/contest/' + self.contest_code + '/problem/' + problem_code
        else:
            print("Could not construct page url.")
            exit(0)
        return None

    def get_test_cases(self, problem_code):
        '''
            Description:
                Given the HTML page data of the problem that we want to work on 
                this function parses the data to get the test cases and create the
                input and output files and store them in a respective folder.
            I/O:
                problem_page_data
            O/P:
                test cases file
        '''
        page_data = self.get_page_data(problem_code)
        soup = bs(page_data.text, features = 'html.parser')
        tests = soup.findAll("div", {"class" : "sample-tests"})
        if len(tests) > 0:
            #There are some inputs and output files to be considered    
            test_case_folder = os.path.join(self.cp_dir, problem_code)
            if(not os.path.exists(test_case_folder)):
                os.makedirs(test_case_folder)
            inputs = tests[0].findAll("div" , {"class" : "input"})
            outputs = tests[0].findAll("div" , {"class" : "output"})

            for case in range(len(inputs)):
                data = inputs[case].find('pre').text.strip()
                filename = ("input_%s" % (case + 1))
                with open(os.path.join(test_case_folder,filename), "w") as file_ptr:
                    file_ptr.write(data)

            for case in range(len(outputs)):
                data = outputs[case].find('pre').text.strip()
                filename = ("output_%s" % (case + 1))
                with open(os.path.join(test_case_folder,filename), "w") as file_ptr:
                    file_ptr.write(data)

        else:
            print("No test cases associated with this problem code.")

class CODECHEF(SITE):
    """
        Description:
            This class encapsulates all the properties of the Codechef class
            and how things need to be done for codechef website
    """
    folder = None
    site = "Codechef"
    MAX_TRIES = 5
    url = 'https://www.codechef.com/api'
    def __init__(self, contest_code):
        """
            Description:
                Initialise properties related to the Codechef class
        """
        self.contest_code = (contest_code if contest_code else 'PRACTICE')
        #   Check whether necessary folder structure is in place or not
        #   So that the test files could be saved there
        self.cp_dir = (os.path.join(CODECHEF.folder, self.contest_code))
        if(not os.path.exists(self.cp_dir)):
            os.makedirs(self.cp_dir)


    def construct_problem_url(self, problem_code):
        if problem_code:
            return (self.url + "/contests/" + self.contest_code + '/problems/' + problem_code)
        else:
            print("Could not construct page url.")
            exit(0)
        return None
    
    
    def get_test_cases(self, problem_code):
        """
            Codechef site has data in a variety of format.
            This function parses test cases from most of the formats.
        """
        try:
            response = self.get_page_data(problem_code)
            page_data = response.json()
            page_data = page_data['body']
            data_list = page_data.split("```")
            page_data = "</pre>".join("<pre>".join(data_list[i:i + 2]) for i in range(0, len(data_list), 2))
            soup = bs(page_data, "html.parser")
            test_pre_list = soup.find_all('pre')
            test_cases = []
            for each_pre in test_pre_list:
                tt_tags = each_pre.find_all('tt')
                if len(tt_tags) == 2:
                    test_cases.append((tt_tags[0].text, tt_tags[1].text))
                code_tags = each_pre.find_all('code')
                if len(code_tags) == 2:
                    test_cases.append((code_tags[0].text, code_tags[1].text))
                    
            if len(test_cases) == 0:
                for each_pre in test_pre_list:
                    # print(each_pre)
                    b_tags = each_pre.find_all('b')
                    if len(b_tags) == 2:
                        test_cases.append((b_tags[0].nextSibling, b_tags[1].nextSibling))
                

            if len(test_cases) == 0:
                current = 0
                while(current < len(test_pre_list)):
                    text_one = str(test_pre_list[current].text)
                    constr_regex = "-?[0-9]+\ *((≤|<=|<)\ *[\w<>//|]+\ *)+\ *(≤|<|<=)\ *-?[0-9]+"
                    if (re.search(constr_regex, text_one)):
                        #We need to skip this pre as this is a constraint
                        current += 1
                    else:
                        text_two = str(test_pre_list[current + 1].text)
                        if(re.search("input", text_one, re.IGNORECASE)):
                            text_one = "\n".join(text_one.split("\n")[2:])
                        if(re.search("output", text_two, re.IGNORECASE)):
                            text_two = "\n".join(text_two.split("\n")[2:])
                        test_cases.append((text_one, text_two))
                        current += 2
            
            for pos in range(len(test_cases)):
                test_cases[pos] = (test_cases[pos][0].strip(), test_cases[pos][1].strip())
            
            
            if len(test_cases):    
                test_case_folder = os.path.join(self.cp_dir, problem_code)
                if(not os.path.exists(test_case_folder)):
                    os.makedirs(test_case_folder)
                for case in range(len(test_cases)):
                    data = test_cases[case][0]
                    filename = ("input_%s" % (case + 1))
                    with open(os.path.join(test_case_folder,filename), "w") as file_ptr:
                        file_ptr.write(data)
                    data = test_cases[case][1]
                    filename = ("output_%s" % (case + 1))
                    with open(os.path.join(test_case_folder,filename), "w") as file_ptr:
                        file_ptr.write(data)
            else:
                print("No test cases available for this problem.")        
        
        except (KeyError, ValueError):
            print("Error: Incorrect data received.")
            exit(0)