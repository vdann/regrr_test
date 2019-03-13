
var Utils = (function () {

	var regex_email = /^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/gm;
	function isValidEmail(str) {
		var isOk = str.search(regex_email) != -1;
		return isOk;
	}

	//------------------------------------
	var validators = {};
	validators.isValidEmail = isValidEmail;


	//------------------------------------
	var icons = {};
	icons.ok = 'fa fa-2x fa-check clr-green';
	icons.fail = 'fa fa-2x fa-exclamation-triangle clr-red';
	icons.wait = 'fa fa-2x fa-refresh fa-spin clr-blue';

	return {
		validators : validators,
		icons: icons
	}
})();