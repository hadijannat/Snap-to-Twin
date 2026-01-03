use wasm_bindgen::prelude::*;
use serde::{Serialize, Deserialize};

// --- 1. Minimal AAS V3.0 Data Model ---
// This follows the Asset Administration Shell specification for Industry 4.0
// https://www.plattform-i40.de/IP/Redaktion/EN/Standardartikel/specification-administrationshell.html

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SubmodelElement {
    pub id_short: String,
    pub value: String,
    pub unit: Option<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AssetAdministrationShell {
    pub id: String,
    pub asset_type: String,
    pub nameplate: Vec<SubmodelElement>,
}

// --- 2. The Active Twin Class ---
// This is the "executable" digital twin that runs in WebAssembly
// It combines passive data (AAS JSON) with active behavior (simulation, queries)

#[wasm_bindgen]
pub struct DigitalTwin {
    data: AssetAdministrationShell,
    // Internal state for simulation (demonstrates "live" twin behavior)
    rpm_sim: f64,
    tick_count: u32,
}

#[wasm_bindgen]
impl DigitalTwin {
    /// Constructor: Hydrates the twin from an AAS JSON string
    /// This is called from JavaScript when loading twin_config.json
    #[wasm_bindgen(constructor)]
    pub fn new(json_config: &str) -> Result<DigitalTwin, JsValue> {
        let data: AssetAdministrationShell = serde_json::from_str(json_config)
            .map_err(|e| JsValue::from_str(&format!("Invalid AAS JSON: {}", e)))?;

        Ok(DigitalTwin {
            data,
            rpm_sim: 0.0,
            tick_count: 0,
        })
    }

    /// Export standard AAS JSON (for interoperability with other Industry 4.0 tools)
    pub fn get_aas_json(&self) -> String {
        serde_json::to_string_pretty(&self.data).unwrap_or_else(|_| "{}".to_string())
    }

    /// Query a specific property from the nameplate (e.g., "Voltage", "RPM")
    /// This demonstrates structured data access following AAS semantics
    pub fn get_property(&self, name: &str) -> String {
        if let Some(elem) = self.data.nameplate.iter().find(|e| e.id_short == name) {
            return format!("{} {}", elem.value, elem.unit.as_deref().unwrap_or(""));
        }
        format!("Property '{}' not found", name)
    }

    /// Get the asset identifier
    pub fn get_id(&self) -> String {
        self.data.id.clone()
    }

    /// Get the asset type (manufacturer + model)
    pub fn get_asset_type(&self) -> String {
        self.data.asset_type.clone()
    }

    /// List all available properties
    pub fn list_properties(&self) -> String {
        self.data
            .nameplate
            .iter()
            .map(|e| e.id_short.clone())
            .collect::<Vec<_>>()
            .join(", ")
    }

    /// Simulate "live" data (demonstrates active twin behavior)
    /// In a real system, this could connect to sensor data or PLC interfaces
    pub fn tick_simulation(&mut self) -> String {
        self.tick_count += 1;

        // Simulate varying RPM with some realistic variation
        self.rpm_sim += 10.5 + (self.tick_count as f64 * 0.3).sin() * 5.0;

        format!("Live RPM: {:.2} (tick: {})", self.rpm_sim, self.tick_count)
    }

    /// Reset simulation state
    pub fn reset_simulation(&mut self) {
        self.rpm_sim = 0.0;
        self.tick_count = 0;
    }

    /// Get a summary of the twin
    pub fn get_summary(&self) -> String {
        format!(
            "Asset: {}\nType: {}\nProperties: {}",
            self.data.id,
            self.data.asset_type,
            self.list_properties()
        )
    }
}

// --- 3. Module-level functions for utilities ---

/// Validate if a JSON string is a valid AAS configuration
#[wasm_bindgen]
pub fn validate_aas_json(json_str: &str) -> bool {
    serde_json::from_str::<AssetAdministrationShell>(json_str).is_ok()
}

/// Get the library version
#[wasm_bindgen]
pub fn get_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_aas_deserialization() {
        let json = r#"{
            "id": "TEST-001",
            "asset_type": "TestMotor 3000",
            "nameplate": [
                {"id_short": "Voltage", "value": "400", "unit": "V"}
            ]
        }"#;

        let aas: AssetAdministrationShell = serde_json::from_str(json).unwrap();
        assert_eq!(aas.id, "TEST-001");
        assert_eq!(aas.nameplate.len(), 1);
    }

    #[test]
    fn test_digital_twin_creation() {
        let json = r#"{
            "id": "MOTOR-12345",
            "asset_type": "Siemens 1LE1",
            "nameplate": [
                {"id_short": "Voltage", "value": "400", "unit": "V"},
                {"id_short": "Power", "value": "7.5", "unit": "kW"}
            ]
        }"#;

        let twin = DigitalTwin::new(json).unwrap();
        assert_eq!(twin.get_id(), "MOTOR-12345");
        assert!(twin.get_property("Voltage").contains("400"));
    }
}
