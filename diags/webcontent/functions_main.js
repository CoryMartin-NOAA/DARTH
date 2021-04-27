<!--

/* ============================================================================================================= */
/* Preloading & displaying functions */
/* ============================================================================================================= */

//Populate the dropdown menu with items
function populateMenu(mode){
    if(mode == 'channel'){
            var element = document.getElementById("channel");
            for(i = element.options.length - 1 ; i >= 0 ; i--){element.remove(i);}

            for(i=0; i<channels.length; i++){
                    var option = document.createElement("option");
                    option.text = channels[i].displayName;
                    option.value = channels[i].name;
                    element.add(option);
            }
    }
    else if(mode == 'validtime'){
            var element = document.getElementById("validtime");
            for(i = element.options.length - 1 ; i >= 0 ; i--){element.remove(i);}

            for(i=0; i<validtimes.length; i++){
                    var option = document.createElement("option");
                    option.text = validtimes[i].displayName;
                    option.value = validtimes[i].name;
                    element.add(option);
            }
    }
        element.style.fontSize = "16px";
}

//Format URL to the requested domain, variable, run & frame
function getURL1(channel,validtime){
	var newurl = url1.replace("NNN",channel);
	newurl = newurl.replace("CCC",cycle);
	return newurl;
}

//Search for a name within an object
function searchByName(keyname, arr){
    for (var i=0; i < arr.length; i++){
        if (arr[i].name === keyname){
            return i;
        }
    }
	return -1;
}

//Display the current image object
function showImage(){

	//Variable index
	var idx_cyc = searchByName(imageObj.validtime,validtimes);

	//Update user on whether image is still loading
	if(validtimes[idx_cyc].images[imageObj.frame].loaded == false){
		document.getElementById('loading').style.display = "block";
	}
	else{
		document.getElementById('loading').style.display = "none";
		document.map.src = validtimes[idx_cyc].images[imageObj.frame].src;
    document.map2.src = validtimes[idx_cyc].images[imageObj.frame].src;
	}

	//Update dropdown menus
  document.getElementById("channel").selectedIndex = searchByName(imageObj.channel,channels);
  document.getElementById("validtime").selectedIndex = searchByName(imageObj.validtime,validtimes);

	//Update URL in address bar
	generate_url();
}

//Preload images for the current run, variable & projection
function preload(obj){

	//Variable index
	var idx_cyc = searchByName(obj.validtime,validtimes);

	validtimes[idx_cyc].images[i] = [];

	//Arrange list of hour indices to loop through
	var frameidx = frames.indexOf(imageObj.frame);
	var hrs_loop = [frameidx];

	for(i=1; i<frames.length; i++){

		var idx_up = frameidx + i;
		var idx_down = frameidx - i;

		if(idx_up<=frames.indexOf(maxFrame)){hrs_loop.push(idx_up);}
		if(idx_down>=frames.indexOf(minFrame)){hrs_loop.push(idx_down);}
	}

	//Loop through all forecast hours & pre-load image
	for (i2=0; i2<hrs_loop.length; i2++){
		var i1 = hrs_loop[i2];
		var i = frames[i1];

		var urls1 = getURL1(obj.channel,obj.validtime);

		validtimes[idx_cyc].images[i] = new Image();
		validtimes[idx_cyc].images[i].loaded = false;
		validtimes[idx_cyc].images[i].id = i;
		validtimes[idx_cyc].images[i].onload = function(){this.loaded = true; remove_loading(this.varid,this.id);};
		validtimes[idx_cyc].images[i].onerror = function(){remove_loading(this.varid,this.id); this.src='https://www.emc.ncep.noaa.gov/users/verification/global/gfs/ops/images/noimage.png';};
		validtimes[idx_cyc].images[i].src = urls1;
		validtimes[idx_cyc].images[i].validtime = obj.validtime;
		validtimes[idx_cyc].images[i].varid = idx_cyc;
    }
}

//Remove sign of loading image
function remove_loading(idx_cyc,idx_frame){
	check1a = parseInt(idx_cyc);
	check1b = searchByName(imageObj.validtime,validtimes);
	check2a = frames.indexOf(parseInt(idx_frame));
	check2b = frames.indexOf(parseInt(imageObj.frame));

	//Remove if the image just loaded for the currently displayed image
	if((check1a == check1b) && (check2a == check2b)){
		document.getElementById('loading').style.display = "none";
		document.map.src = validtimes[idx_cyc].images[imageObj.frame].src;
    document.map2.src = validtimes[idx_cyc].images[imageObj.frame].src;
	}
}

/* ============================================================================================================= */
/* Dropdown menu functions */
/* ============================================================================================================= */

//Change the map level from dropdown menu
function changeChannel(id){
        imageObj.channel = id;
        preload(imageObj);
        showImage();
        document.getElementById("channel").blur();
}

//Change the map validtime from dropdown menu
function changeValidtime(id){
        imageObj.validtime = id;
        preload(imageObj);
        showImage();
        document.getElementById("validtime").blur();
}

/* ============================================================================================================= */
/* Keyboard controls */
/* ============================================================================================================= */

function keys(e){
	//Left
	if(e.keyCode == 37){
		prevFrame();
		return !(e.keyCode);
	}
	//Up
	else if(e.keyCode == 38){
		pressUp();
		return !(e.keyCode);
	}
	//Right
	else if(e.keyCode == 39){
		nextFrame();
		return !(e.keyCode);
	}
	//Down
	else if(e.keyCode == 40){
		pressDown();
		return !(e.keyCode);
	}
}

function prevFrame(){
//	var curFrame = parseInt(imageObj.frame);
//	if(curFrame > minFrame){curFrame = curFrame - incrementFrame;}
//	changeValid(curFrame);
	var curVar = searchByName(imageObj.validtime,validtimes);
	if(curVar > 0){curVar = curVar - 1; changeValidtime(validtimes[curVar].name);}
//	changeLevel(curFrame);
}

function nextFrame(){
//	var curFrame = parseInt(imageObj.frame);
//	if(curFrame < maxFrame){curFrame = curFrame + incrementFrame;}
//	changeValid(curFrame);
	var curVar = searchByName(imageObj.validtime,validtimes);
	if(curVar < validtimes.length-1){curVar += 1; changeValidtime(validtimes[curVar].name);}
}

function pressDown(){
	var curVar = searchByName(imageObj.channel,channels);
	if(curVar < channels.length-1){curVar += 1; changeChannel(channels[curVar].name);}
}

function pressUp(){
	var curVar = searchByName(imageObj.channel,channels);
	if(curVar > 0){curVar = curVar - 1; changeChannel(channels[curVar].name);}
}

/* ============================================================================================================= */
/* Additional functions */
/* ============================================================================================================= */

//Update the URL in the address bar by the current domain and variable
function generate_url(){

	var url = window.location.href.split('?')[0] + "?";
	var append = "";

	//Add channel
	append += "channel=" + imageObj.channel;

	//Add validtime
	append += "&validtime=" + imageObj.validtime;

	//Get new URL
	var total = url + append;

	//Update in address bar without reloading page
	var pagename = window.location.href.split('/');
	pagename = pagename[pagename.length-1];
	pagename = pagename.split(".html")[0];
	var stateObj = { foo: "bar" };
	history.replaceState(stateObj, "", pagename+".html?"+append);

	return total;
}

function updateMobile(){
	if( navigator.userAgent.match(/Android/i)
	|| navigator.userAgent.match(/webOS/i)
	|| navigator.userAgent.match(/iPhone/i)
	|| navigator.userAgent.match(/iPod/i)
	//|| navigator.userAgent.match(/iPad/i)
	|| navigator.userAgent.match(/BlackBerry/i)
	|| navigator.userAgent.match(/Windows Phone/i)
	){
		document.getElementById('page-middle').innerHTML = "Swipe Left/Right on Image = Change forecast lead | Swipe Up/Down on Image = Change level";
	}


	//Swipe for mobile devices only when focused on image
	var element = document.getElementsByName("map")[0];
	element.addEventListener("touchstart", touchStart, false);
	element.addEventListener("touchend", touchEnd, false);
	element.addEventListener("touchmove", touchMove, false);

}

function touchStart(e){
    xInit = e.touches[0].clientX;
    yInit = e.touches[0].clientY;
};

function touchMove(e){
	e.preventDefault();
    xPos = e.touches[0].clientX;
    yPos = e.touches[0].clientY;
};

function touchEnd() {
    if ( ! xPos || ! yPos ) {
        return;
    }

    //Get difference in x & y positions
    var xDiff = xInit - xPos;
    var yDiff = yInit - yPos;

	//Determine whether swipe was vertical or horizontal
    if ( Math.abs(xDiff) > Math.abs(yDiff) ){
        if( xDiff > 0 ){
            //Left swipe
			nextFrame();
        }
		else{
            //Right swipe
			prevFrame();
        }
    }
	else{
        if ( yDiff > 0 ){
            //Up swipe
			pressDown();
        }
		else{
            //Down swipe
			pressUp();
        }
    }

    //reset values
    xInit = null;
    yInit = null;
	xPos = null;
	yPos = null;
};

-->
