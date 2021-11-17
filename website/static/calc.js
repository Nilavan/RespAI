let base64Image;
$("#image-selector").change(function () {
    let reader = new FileReader();
    reader.onload = function (e) {
        let dataURL = reader.result;
        $("#selected-image").attr("src", dataURL);
        base64Image = dataURL.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
        console.log(base64Image);
    };
    reader.readAsDataURL($("#image-selector")[0].files[0]);
    $("#result").text("");
    $("#probability").text("");
});

//$("#predict-button").click(function () {
//    let message = {
//      image: base64Image,
//    };

//    console.log(message);
//    $.post("/", JSON.stringify(message), function (response) {
//       $("#result").text(response.prediction.result);
//        $("#probability").text(response.prediction.accuracy.toFixed(2));
//        console.log(response);
//   });
//});

function verify() {
    
}