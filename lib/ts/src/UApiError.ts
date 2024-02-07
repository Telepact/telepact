/**
 * Indicates critical failure in uAPI processing logic.
 */
class UApiError extends Error {
    constructor(message: string);
    constructor(cause: Error);
    constructor(arg: string | Error) {
      super(typeof arg === 'string' ? arg : arg.message);
  
      if (typeof arg !== 'string') {
        this.stack = arg.stack;
      }
    }
  }
  