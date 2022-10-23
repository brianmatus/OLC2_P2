$("#runCode").click(function () {
    let code = $("#codeTextArea").val();
    //console.log(code)
    
  $.post("http://127.0.0.1:5000/parse_code",
  {
    code: code,
      a: 24
  },
  function(data, status){
      var result = data.result
      console.log("resultado:")
      console.log(result)

      $("#outputTextArea").val(result.console_output);
      
      
      var allError = result.lexic_errors.concat(result.syntactic_errors, result.semantic_errors);
      
      $("#errorTable tbody").html(makeErrorTableHTML(allError));
      $("#symbolTable tbody").html(makeSymbolTableHTML(result.symbol_table));
      $("#optimizationTable tbody").html(makeOptTableHTML(result.optimization));
      
      
      // var options = {
      //   format: 'svg'
      //     // format: 'png-image-element'
      //   }
      // var image = Viz(result.astTree, options);
      // var astTreeDiv = document.getElementById('astTreeDiv');
      // astTreeDiv.innerHTML = image;

      
  });
    
    
})


function makeOptTableHTML(myArray) {
    console.log("makeOptTableHTML")
    console.log(myArray)
    var result = "";
    for(var i=0; i<myArray.length; i++) {

        element = myArray[i].split("<->")
        console.log(element)

        result += "<tr>";
        result += "<td>"+element[0]+"</td>";
        result += "<td>"+element[1]+"</td>";
        result += "<td>"+element[2]+"</td>";
        
        result += "</tr>";
    }
    result += "</table>";

    return result;
}


function makeErrorTableHTML(myArray) {
    console.log("makeErrorTableHTML")
    console.log(myArray)
    var result = "";
    for(var i=0; i<myArray.length; i++) {

        element = myArray[i].split("<->")
        console.log(element)

        result += "<tr>";
        result += "<td>"+element[0]+"</td>";
        result += "<td>"+element[1]+"</td>";
        result += "<td>"+element[2]+"</td>";
        
        result += "</tr>";
    }
    result += "</table>";

    return result;
}


function makeSymbolTableHTML(myArray) {
    var result = "";
    for(var i=0; i<myArray.length; i++) {
        result += "<tr>";
        for(var j=0; j<myArray[i].length; j++){
            result += "<td>"+myArray[i][j]+"</td>";
        }
        result += "</tr>";
    }
    result += "</table>";
    return result;
}
