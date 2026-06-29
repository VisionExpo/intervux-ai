export class Logger {
    public info(message: string, ...args: any[]): void {
        console.log(`[INFO] ${message}`, ...args);
    }

    public warn(message: string, ...args: any[]): void {
        console.warn(`[WARN] ${message}`, ...args);
    }

    public error(message: string, ...args: any[]): void {
        console.error(`[ERROR] ${message}`, ...args);
    }

    public debug(message: string, ...args: any[]): void {
        console.debug(`[DEBUG] ${message}`, ...args);
    }
}
