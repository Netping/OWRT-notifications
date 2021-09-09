function slug(str) {
	var result = ''
	const ru = new Map([
		['а', 'a'], ['б', 'b'], ['в', 'v'], ['г', 'g'], ['д', 'd'], ['е', 'e'],
		['є', 'e'], ['ё', 'e'], ['ж', 'j'], ['з', 'z'], ['и', 'i'], ['ї', 'yi'], ['й', 'i'],
		['к', 'k'], ['л', 'l'], ['м', 'm'], ['н', 'n'], ['о', 'o'], ['п', 'p'], ['р', 'r'],
		['с', 's'], ['т', 't'], ['у', 'u'], ['ф', 'f'], ['х', 'h'], ['ц', 'c'], ['ч', 'ch'],
		['ш', 'sh'], ['щ', 'shch'], ['ы', 'y'], ['э', 'e'], ['ю', 'u'], ['я', 'ya'],
	]);

	str = str.replace(/[ъь]+/g, '');
	str = str.replace(/\s+/g, '_');


	result = Array.from(str)
		.reduce((s, l) =>
			s + (
				  ru.get(l)
				  || ru.get(l.toLowerCase()) === undefined && l
				  || ru.get(l.toLowerCase())
			  )
			, '');
	result = result.replace(/[^A-Za-z0-9_]/g, '');
	return result;
}

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}


// make "2020-11-30" from "30.11.2020
function normDateString(s) {
	return s.split(".").reverse().join("-");
}