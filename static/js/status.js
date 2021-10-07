
 function checkStatus(){
            if(document.getElementById('status-0').checked) {
            document.getElementById('gender').parentElement.style = "display:visible;";
            document.getElementById('service').parentElement.style = "display:none;";
            document.getElementById('birth_date').parentElement.style = "display:visible;";
            document.getElementById('company_url').parentElement.style = "display:none;";

           }
          else if(document.getElementById('status-1').checked) {
          document.getElementById('gender').parentElement.style = "display:none;";
          document.getElementById('service').parentElement.style = "display:visible;";
          document.getElementById('birth_date').parentElement.style = "display:none;";
          document.getElementById('company_url').parentElement.style = "display:visible;";
    }}
    function intial_status(){
    document.getElementById('gender').parentElement.style = "display:none;";
      document.getElementById('service').parentElement.style = "display:none;";
        document.getElementById('birth_date').parentElement.style = "display:none;";
        document.getElementById('company_url').parentElement.style = "display:none;";
}
intial_status();
checkStatus();


        function setAttributes(el, attrs) {
            for (var key in attrs) {
                el.setAttribute(key, attrs[key]);
            }
        }



        setAttributes(document.getElementsByClassName('radio')[0], {
            "onclick": "checkStatus()",
            "style": "style=display:block!important; float: left;margin-left:1rem;margin-bottom:2rem;lmargin-top:2rem; ",
            "onload":" checkStatus()"
        });

        setAttributes(document.getElementsByClassName('radio')[1], {
            "onclick": "checkStatus()",
            "style": "style=display:block!important; float: left;margin-left:1rem;margin-bottom:2rem;lmargin-top:2rem; ",
            "onload":" checkStatus()"
        });


        function loading() {
            $("#loading").show();
            $("#content").hide();
        }
  document.getElementById('loading').setAttribute('onclick', 'loading()');
        var helpBlocks = document.getElementsByClassName('help-block');
        for (var i = 0; i < helpBlocks.length; i++) {
            helpBlocks[i].setAttribute('style', 'color:red;');
        }
        document.getElementById('submit').setAttribute('onclick', 'loading()');
        document.getElementsByClassName('form')[0].setAttribute('style', ' style="text-align:center !important;');
        document.getElementById('status-0').setAttribute('style', 'display:block !important;margin-left:1rem;margin-right:1rem;margin-top:0.5rem;margin-bottom:0;padding:0px 0px ');
        document.getElementById('status-1').setAttribute('style', 'display:block !important;margin-left:1rem;margin-right:1rem;margin-top:0.5rem;margin-bottom:0;padding:0px 0px ');
