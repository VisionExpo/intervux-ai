import { ReplaySerializer } from "./ReplaySerializer";

/**
 * Isomorphic hasher using Web Crypto API.
 * Returns a SHA-256 hex string.
 */
export class SnapshotHasher {
    public static async hash(obj: any): Promise<string> {
        const canonicalString = ReplaySerializer.serialize(obj);
        return this.hashString(canonicalString);
    }

    public static async hashString(message: string): Promise<string> {
        // We use the Web Crypto API, which is available in Browser and Node 18+
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        
        // Convert buffer to hex string
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        return hashHex;
    }
}
