
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
	// icons
	var icons = {};
	icons.ok = 'fa fa-2x fa-check clr-green';
	icons.fail = 'fa fa-2x fa-exclamation-triangle clr-red';
	icons.wait = 'fa fa-2x fa-refresh fa-spin clr-blue';

	export_.icons = icons;

	//------------------------------------
	// html
	function nbsp(s) {
		return s.replace(/ /g, '&nbsp;');
	}

	function b(s) {
		return '<b>' + s + '</b>';
	}

	function a(href, text) {
		return '<a href="' + href + '">' + text + '</a>';
	}

	export_.html = {
		nbsp: nbsp,
		b: b,
		a: a
	};


	//------------------------------------
	// text
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
	// routes
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

	//------------------------------------
	// rules

	function str_to_num(s) {
		s = s.replace(new RegExp(',', 'gm'), '.');
		return +s;
	}

	function desc(value, is_valid, is_fail) {
		return {
			is_valid: is_valid,
			is_fail: is_fail,
			value_str: value,
			value_format: value
		};
	}


	function value_get_desc(item) {

		if (item.type == 'RANGE') {
			var v = str_to_num(item.value);
			if (isNaN(v))
				return desc(item.value);

			if (item.v1 > v || item.v2 < v)
				return desc(v.toFixed(item.digits), true, true);

			return desc(v.toFixed(item.digits), true);
		}

		if (item.type == 'LESS') {
			var v = str_to_num(item.value);
			if (isNaN(v))
				return desc(item.value);

			if (item.v1 < v)
				return desc(v.toFixed(item.digits), true, true);

			return desc(v.toFixed(item.digits), true);
		}


		if (item.type == 'MORE') {
			var v = str_to_num(item.value);
			if (isNaN(v))
				return desc(item.value);

			if (item.v1 > v)
				return desc(v.toFixed(item.digits), true, true);

			return desc(v.toFixed(item.digits), true);
		}

		if (item.type == 'NEG') {
			var v = str_to_num(item.value);
			if (isNaN(v))
				return desc(item.value);

			if (v > 0)
				return desc(v.toFixed(item.digits), true, true);

			return desc(v.toFixed(item.digits), true);
		}

		if (item.type == 'ANY') {
			return desc(item.value, true);
		}

		if (item.type == 'STR') {
			var v = item.value.toLowerCase();
			return desc(v, true, item.v1.toLowerCase() != v);
		}

		throw 'Неизвестный тип правила: ' + item.type;
		return desc(item.value);
	}


	function value_get_descformat(item) {
		var v = value_get_desc(item);

		if (!v.is_valid)
			v.value_format = '<i>' + v.value_str + '</i>';
		else if (v.is_fail)
			v.value_format = '<b>' + v.value_str + '</b>';

		return v;
	}


	export_.rules = {
		str_to_num: str_to_num,
		value_get_desc: value_get_desc,
		value_get_descformat: value_get_descformat
	};

	//------------------------------------
	return export_;
})();