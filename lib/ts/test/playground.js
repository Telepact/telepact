const _utilTypes = require("../lib/src/_utilTypes");
const { _RandomGenerator } = _utilTypes;

var r = new _RandomGenerator(3, 3);
for (var i = 0; i < 100; i += 1) {
    r.nextInt();
    console.log(r.seed);
}
