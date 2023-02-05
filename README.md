# Weight-Estimation

## 📝 Problem Statement

At a last mile hub, setup a tool or application that has the ability to measure the dimensions (_length, breadth and height_) and capture volumetric weights by image, depth or any sensory processing as required. The tool will scan an item placed before it one by one, and estimate the volumetric weight provided that same items are expected to have similar volumetric weight.

Tool will be assisted with a barcode or qr scanner to identify the items (with barcoding or qr code scanning not being the scope of the problem). If similar items do not have the weight or dimensions within a range of accepted error, such items should be **flagged as erroneous**.

## :skull::weight_lifting: Dead Weight Estimation

<p align="center"> 
<img src="images/dead-weight-simulation.gif" alt="Animated gif of spam clasffication" height="382px">
</p>

### :toolbox: Components Used

| Item Name                     | Purpose                                          | Qty |
| ----------------------------- | ------------------------------------------------ | --- |
| Arduino Nano                  | Central Processing Unit                          | 1   |
| Weighing Load Cell            | Converts force into electric signal (transducer) | 4   |
| Hx711 Weight Pressure Sensor  | Amplification of electrical signals              | 1   |
| Liquid Crystal Display 1602   | Output                                           | 1   |
| 12V Li-Ion Battery            | Input Power Supply                               | 1   |
| 12V to 3.3V Voltage Convertor | Stepping-down voltage                            | 1   |
| Wires and PCB                 | Connection                                       | -   |

### :hammer_and_wrench: Circuit Diagram

<p align = "center">
<img src="images/circuit.png" style="width:70%; height:80%;"/>
</p>

### :gear: Physical Setup of Weight Machine

<p align = "center">
<img src="images/top-view.jpg" style="width:40%; height:45%;"/>
</p>
<p align = "center">
  <i>Top-View of the Weight Machine (315 grams Multimeter being measured)</i>
</p>

<p align = "center">
<img src="images/side-view.jpg" style="width:50%; height:65%;"/>
</p>
<p align = "center">
  <i>Side-View of the Weight Machine (Load cells at bottom of the plate)</i>
</p>

## :potable_water: Volumetric Weight Estimation

### :toolbox: Components Used

| Item Name                           | Purpose                   | Qty |
| ----------------------------------- | ------------------------- | --- |
| Arduino Nano                        | Central Processing Unit   | 1   |
| SHARP Infrared Sensor[GP2Y0A41SK0F] | Distance Measuring Sensor | 1   |
| Liquid Crystal Display 1602         | Output                    | 1   |
| 12V Li-ION Battery                  | Input Power Supply        | 1   |
| 12 V to 3.3 V Voltage Converter     | Stepping-down Voltage     | 1   |
| Wires and PCB                       | Connection                | 1   |

### Running the container:

1. `cd '.\Volumetric Weight Estimation\'`
2. `docker build -t weight_estimation .`
3. `docker run -d -p 5000:5000 weight_estimation2`

### API Documentation:

**1. Get Volume and other details from an image file:**

- **URL**: http://localhost:5000/volume/fromFile

- **Method:** `POST`
- **Request**

  The request body should contain a payload of type `form-data` having the following properties:
  | key | value |
  |:---:|:----:|
  | file| image (file buffer) |

  Supported image formats include `png`, `jpg` and `jpeg`.

- **Success Response:**

  - **Code:** 201 <br />
    **Content:**
    ```python
    {
      "area": float,
      "breadth": float,
      "length": float
    }
    ```

- **Error Response:**

  - **Code:** 406 <br />
    **Content:**

    ```python
    {
      "message": "Poor Lightning Conditions, Fix and Try Again"
    }
    ```

  - **Code:** 400
    ```python
    {
      "message": "No file part in the request"
    }
    ```

**2. Get Volume and other details from Base64-encoded string:**

- **URL**: http://localhost:5000/volume/fromBase64

- **Method:** `POST`
- **Request**

  The request body should contain a `json` payload having the following properties:
  | key | value |
  |:---:|:----:|
  | file| Base64-encoded string of the image's data |

- **Success Response:**

  - **Code:** 201
    ```python
    {
      "area": float,
      "breadth": float,
      "length": float
    }
    ```

- **Error Response:**

  - **Code:** 406

    ```python
    {
      "message": "Poor Lightning Conditions, Fix and Try Again"
    }
    ```

  - **Code:** 400
    ```python
    {
      "message": "JSON payload not found"
    }
    ```
