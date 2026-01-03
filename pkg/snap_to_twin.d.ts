/* tslint:disable */
/* eslint-disable */

export class DigitalTwin {
  free(): void;
  [Symbol.dispose](): void;
  /**
   * Get a summary of the twin
   */
  get_summary(): string;
  /**
   * Export standard AAS JSON (for interoperability with other Industry 4.0 tools)
   */
  get_aas_json(): string;
  /**
   * Query a specific property from the nameplate (e.g., "Voltage", "RPM")
   * This demonstrates structured data access following AAS semantics
   */
  get_property(name: string): string;
  /**
   * Get the asset type (manufacturer + model)
   */
  get_asset_type(): string;
  /**
   * List all available properties
   */
  list_properties(): string;
  /**
   * Simulate "live" data (demonstrates active twin behavior)
   * In a real system, this could connect to sensor data or PLC interfaces
   */
  tick_simulation(): string;
  /**
   * Reset simulation state
   */
  reset_simulation(): void;
  /**
   * Constructor: Hydrates the twin from an AAS JSON string
   * This is called from JavaScript when loading twin_config.json
   */
  constructor(json_config: string);
  /**
   * Get the asset identifier
   */
  get_id(): string;
}

/**
 * Get the library version
 */
export function get_version(): string;

/**
 * Validate if a JSON string is a valid AAS configuration
 */
export function validate_aas_json(json_str: string): boolean;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
  readonly memory: WebAssembly.Memory;
  readonly __wbg_digitaltwin_free: (a: number, b: number) => void;
  readonly digitaltwin_get_aas_json: (a: number) => [number, number];
  readonly digitaltwin_get_asset_type: (a: number) => [number, number];
  readonly digitaltwin_get_id: (a: number) => [number, number];
  readonly digitaltwin_get_property: (a: number, b: number, c: number) => [number, number];
  readonly digitaltwin_get_summary: (a: number) => [number, number];
  readonly digitaltwin_list_properties: (a: number) => [number, number];
  readonly digitaltwin_new: (a: number, b: number) => [number, number, number];
  readonly digitaltwin_reset_simulation: (a: number) => void;
  readonly digitaltwin_tick_simulation: (a: number) => [number, number];
  readonly get_version: () => [number, number];
  readonly validate_aas_json: (a: number, b: number) => number;
  readonly __wbindgen_externrefs: WebAssembly.Table;
  readonly __wbindgen_free: (a: number, b: number, c: number) => void;
  readonly __wbindgen_malloc: (a: number, b: number) => number;
  readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
  readonly __externref_table_dealloc: (a: number) => void;
  readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
* Instantiates the given `module`, which can either be bytes or
* a precompiled `WebAssembly.Module`.
*
* @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
*
* @returns {InitOutput}
*/
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
* If `module_or_path` is {RequestInfo} or {URL}, makes a request and
* for everything else, calls `WebAssembly.instantiate` directly.
*
* @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
*
* @returns {Promise<InitOutput>}
*/
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
