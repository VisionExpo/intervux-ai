export class ReplaySerializer {
    /**
     * Canonicalizes an object by:
     * 1. Sorting keys alphanumerically (to guarantee deterministic serialization).
     * 2. Removing known non-deterministic fields (like timestamps, auto-gen IDs).
     */
    public static canonicalize(obj: any): any {
        if (obj === null || obj === undefined) return obj;

        if (Array.isArray(obj)) {
            return obj.map(item => this.canonicalize(item));
        }

        if (typeof obj === 'object') {
            const keys = Object.keys(obj).sort();
            const result: any = {};
            
            for (const key of keys) {
                // Strip timestamps or known non-deterministic transient state
                if (key === 'timestamp' || key === 'generatedAt' || key === 'lastUpdated') {
                    continue;
                }
                result[key] = this.canonicalize(obj[key]);
            }
            return result;
        }

        return obj;
    }

    public static serialize(obj: any): string {
        return JSON.stringify(this.canonicalize(obj));
    }
}
