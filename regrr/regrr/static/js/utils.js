
var Utils = (function () {

	var export_ = {}

	//------------------------------------
	var regex_email = /^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/gm;
	function isValidEmail(str) {
		var isOk = str.search(regex_email) != -1;
		return isOk;
	}

	//------------------------------------
	var validators = {};
	validators.isValidEmail = isValidEmail;

	export_.validators = validators;


	//------------------------------------
	var icons = {};
	icons.ok = 'fa fa-2x fa-check clr-green';
	icons.fail = 'fa fa-2x fa-exclamation-triangle clr-red';
	icons.wait = 'fa fa-2x fa-refresh fa-spin clr-blue';

	export_.icons = icons;

	//------------------------------------
	function nbsp(s) {
		return s.replace(/ /g, '&nbsp;');
	}

	function b(s) {
		return '<b>' + s + '</b>';
	}

	export_.html = {
		nbsp: nbsp,
		b: b
	};


	//------------------------------------
	/*
		var r = declinationOfNumbers(10, ['результат', 'результата', 'результатов']);
		assert(r == 'результатов');
	 */
	function declinationOfNumbers(number, label_1, label_234, label_0_56789) {
		if (_.isArray(label_1)) {
			label_234 = label_1[1];
			label_0_56789 = label_1[2];
			label_1 = label_1[0];
		}

		number = Math.abs(number) % 100;
		if (number > 10 && number < 20) {
			return label_0_56789;
		}

		number = number % 10;
		if (number > 1 && number < 5) {
			return label_234;
		}

		if (number == 1) {
			return label_1;
		}

		return label_0_56789;
	}

	export_.text = {
		declinationOfNumbers: declinationOfNumbers
	};


	//------------------------------------
	/*
	    var route = '/tms/1.0.0/<id>/<z>/<x>/<y>.png';
        var params = {id:'land', z:1, x:2, y:3};
        var url = makeUrlFromRoute(route, params);
		assert(url, '/tms/1.0.0/land/1/2/3.png');
	 */
	function makeUrlFromRoute(route, params) {
		for (key in params) {
			var param = params[key];
			var t = typeof param;
			if (t === 'string' || t === 'number')
				route = route.replace(new RegExp('<' + key + '>', 'gm'), param);
		}

		if (/<\w+(\:\w*)*>/gm.test(route))
			console.warn('makeUrlFromRoute => Не все параметры маршрута заданы', route);

		return route;
	}

	export_.routes = {
		makeUrlFromRoute: makeUrlFromRoute
	};


	return export_;
})();