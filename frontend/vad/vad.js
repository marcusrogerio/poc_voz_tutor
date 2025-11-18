import initWasm, { MicVAD as MicVADClass } from "./processing-wasm.wasm";

export const VAD = {
    async MicVAD(options) {
        await initWasm();
        return MicVADClass.new(options);
    }
};

export default VAD;
