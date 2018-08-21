# Summer2018-generating-synthetic-dataset-from-deidentified-dataset

This is a python project that includes de-identification and synthesis of educational data from DataShop@CMU. (https://pslcdatashop.web.cmu.edu/)


### Overview
- Statistical Analysis: generate meta file for the dataset
- dAFM: deep Additive Factors Model to learn the performance of students on certain problems
- modeler: Learn and de-identify the original dataset
- sampler: Create synthetic data

### Installation
This project depends on the following requirements:
- python3
- pandas
- keras
- theano
- numpy
- scipy
- sklearn
- copulas


### Usage
1) Clone the github repository.
```
git clone https://github.com/dongyanl/Summer2018-Generating-Synthetic-Data-from-Deidentified-Data
```

2) Execute the ```sampler.py``` script using python after specifying the input values. It will summarize and de-identify the original dataset and create the synthetic dataset. The example dataset is already included in the datasets folder.
**Note:** The detailed description of the input values is mentioned in later section.
```
python3 sampler.py --dataset_path Example/example.txt --num_of_stu 5
```

### Input Parameters
The arguements can be passed to the main script py adding them using the syntax given by `python3 sampler.py --arguement_name1  value arguement_name2 value1`.

Arguement Name | Parameters | Description
:--------------------- | :------------- | :--------
**dataset_path** | required | Absolute path of the dataset file or name of file if present in datasets folder
value| dataset_path | default: Example/example.txt
**num_of_stu**| required | number of student-problem generated in synthetic data
value| n | default: 2

### Output Files

**Description**

File Name | Description
:----------------- | :--------
**report.json** | meta file that summarize the original data
**synthetic.csv** | synthetic data


**Preview**

report.json
```
{
    "students": [
        {
            "fields": [
                {
                    "datatype": "int64",
                    "max": 228,
                    "mean": 114.5,
                    "min": 1,
                    "name": "Row",
                    "num of unique values": 228,
                    "std": 65.96211033616193
                },
                {
                    "datatype": "object",
                    "max length": 8,
                    "min length": 8,
                    "name": "Sample Name",
                    "num of unique values": 1,
                    "overlap characters": "All Data",
                    "total num of values": 228
                },
         ...
        }
        ...
}
```
          
