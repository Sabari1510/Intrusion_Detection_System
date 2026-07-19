/* ==========================================
   Network Intrusion Detection System
   Main JavaScript File
========================================== */


/* ==========================================
   Page Load Message
========================================== */

console.log(
    "Network Intrusion Detection System Loaded Successfully"
);



/* ==========================================
   Prediction Page Functions
========================================== */


/*
   CSV Prediction
   Currently using dummy output.
   Later connect with FastAPI /predict API.
*/

function predictCSV(){


    let file = document.getElementById("csvFile");


    if(file.files.length === 0){

        alert("Please upload CSV file");

        return;

    }


    document.getElementById("prediction").innerHTML =
    "Analyzing Network Traffic...";


    setTimeout(()=>{


        let results=[

            "BENIGN",
            "DDoS",
            "DoS Hulk",
            "PortScan",
            "Bot"

        ];


        let prediction =
        results[Math.floor(Math.random()*results.length)];


        document.getElementById("prediction").innerHTML =
        prediction;


    },2000);


}




/*
   Manual Feature Prediction
*/

function predictManual(){


    let flowDuration =
    document.getElementById("flowDuration").value;


    let packetLength =
    document.getElementById("packetLength").value;


    let flowBytes =
    document.getElementById("flowBytes").value;



    if(

        flowDuration === "" ||
        packetLength === "" ||
        flowBytes === ""

    ){

        alert("Please enter all feature values");

        return;

    }



    document.getElementById("prediction").innerHTML =
    "Processing...";



    setTimeout(()=>{


        let predictions=[

            "BENIGN",
            "DDoS",
            "DoS Hulk",
            "PortScan",
            "FTP-Patator"

        ];



        let output =
        predictions[
            Math.floor(Math.random()*predictions.length)
        ];



        document.getElementById("prediction").innerHTML =
        output;



    },1500);



}




/* ==========================================
   Smooth Scroll
========================================== */


document.addEventListener(
"DOMContentLoaded",
()=>{


    const buttons =
    document.querySelectorAll("a");


    buttons.forEach(button=>{


        button.addEventListener(
        "click",
        function(){


            console.log(
            "Navigating to:",
            this.href
            );


        });


    });


});





/* ==========================================
   Future FastAPI Integration Example
========================================== */


/*

async function sendPrediction(data){


    let response =
    await fetch(
    "http://127.0.0.1:8000/predict",
    {

        method:"POST",

        headers:{

            "Content-Type":"application/json"

        },

        body:JSON.stringify(data)

    });


    let result =
    await response.json();


    document.getElementById("prediction").innerHTML =
    result.prediction;


}

*/


/* ==========================================
   End
========================================== */