package uapitest;

import java.util.List;
import java.util.Map;

import uapitest.ServerHandler_;
import uapitest.example.Input;
import uapitest.example.Output;

public class CodeGenHandler extends ServerHandler_ {

    @Override
    public Output example(Map<String, Object> headers, Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'example'");
    }

    @Override
    public uapitest.test.Output test(Map<String, Object> headers, uapitest.test.Input input) {
        var outputBuilder = new uapitest.test.Output.Ok_.Builder();

        input.value.ifPresent(top -> {
            top.any.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().any(v).build());
            });
            top.arr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arr(v).build());
            });
            top.arrAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrAny(v).build());
            });
            top.arrArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrArr(v).build());
            });
            top.arrBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrBool(v).build());
            });
            top.arrFn.ifPresent(v -> {
                List<example.Input> list = v.stream()
                        .map(v1 -> {
                            var b1 = new example.Input.Builder();
                            v1.optional.ifPresent(b1::optional);
                            return b1.build();
                        })
                        .toList();
                outputBuilder.value(new Value.Builder().arrFn(list).build());
            });
            top.arrInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrInt(v).build());
            });
            top.arrNullAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullAny(v).build());
            });
            top.arrNullArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullArr(v).build());
            });
            top.arrNullBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullBool(v).build());
            });
            top.arrNullFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullFn(v).build());
            });
            top.arrNullInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullInt(v).build());
            });
            top.arrNullNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullNum(v).build());
            });
            top.arrNullObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullObj(v).build());
            });
            top.arrNullP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullP2Str(v).build());
            });
        });

        return outputBuilder.build();
    }

    @Override
    public uapitest.getBigList.Output getBigList(Map<String, Object> headers, uapitest.getBigList.Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getBigList'");
    }

}
