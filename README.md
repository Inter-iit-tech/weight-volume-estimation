# Weight-Estimation

## Volumetric Weight Estimation:

### Running the container:
1. `cd '.\Volumetric Weight Estimation\'`
2. `docker build -t weight_estimation .`
3. `docker run -d -p 5000:5000 weight_estimation2`

### API Documentation:
**1. Get Volume and other details:**

* **URL**: http://localhost:5000/volume

* **Method:** `POST`
  
*  **URL Params**

   **Required:**
   
   form-data
    | key | data |
    |:---:|:----:|
    | file| image.jpeg |
    
    (Upload your file here)

* **Success Response:**
  
  * **Code:** 201 <br />
    **Content:** `{
    "area": 83.42484632380285,
    "breadth": 3.68,
    "length": 4.44
}`
