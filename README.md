# **YAML to CSV Converter using Streamlit**  

This project provides a simple **web-based tool** to convert **YAML files** into **CSV format** using **Streamlit**. Users can upload their YAML files, preview the data, and download the converted CSV with ease.  

---

## **Features**
- Upload `.yaml` or `.yml` files for conversion.  
- Preview the converted data in a tabular format.  
- Download the data as a CSV file.  
- Handles errors gracefully for invalid or malformed YAML files.

---

## **Installation**
1. **Clone the repository:**
   ```bash
   git clone https://github.com/habeshaethiopia/Utils
   cd Utils
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pandas pyyaml
   ```

---

## **Usage**
1. **Run the Streamlit app:**
   ```bash
   streamlit run YAML_to_csv.py 
   ```

2. **Open the app** in your browser at:
   ```
   http://localhost:8501
   ```

3. **Upload a YAML file**, preview the data, and click "Download CSV" to get the converted file.

---

## **Project Structure**
```
Utils/
│
├── YAML_to_csv.py           # Main application script
└── README.md        # Documentation (this file)
```

---

## **Example YAML File**
```yaml
- name: John Doe
  age: 30
  occupation: Software Engineer
  skills:
    - Python
    - Go
    - Docker

- name: Jane Smith
  age: 27
  occupation: Data Scientist
  skills:
    - Python
    - SQL
    - Machine Learning
```

---

## **How It Works**
1. The user uploads a YAML file via the **Streamlit interface**.  
2. The app uses **PyYAML** to parse the uploaded file into Python objects.  
3. **Pandas** converts the data into a **DataFrame** for easy manipulation and display.  
4. The user can **preview the DataFrame** and **download it as a CSV file**.

---

## **Known Issues**
- Nested YAML structures may appear as strings in the CSV output.

---

## **License**
This project is licensed under the MIT License.  

---

## **Contributing**
Feel free to submit issues or pull requests to improve the project.  

---

## **Contact**
If you have any questions or need support, please reach out to **Adane Moges** at **adanemoges6@gmail.com**.  

---

Enjoy using the YAML to CSV converter! 🎉
