# OMEGA PRIME CONFIGURATION [v9.1 - Tri-Core]
config = {
    "ai": {
        # PRIMÁRNÍ MOZEK (Legacy pointer pro starší skripty)
        "model": "gemini-2.5-pro",
        
        # HIERARCHIE ODOLNOSTI (Pro -> Flash -> Legacy)
        "fallback_order": [
            "gemini-2.5-pro",    # 1. Nejsilnější PRO
            "gemini-2.5-flash",  # 2. Nejrychlejší ZÁLOHA
            "gemini-2.0-flash"   # 3. Stabilní POSLEDNÍ ZÁCHRANA
        ],
        
        "temperature": 0.7
    },
    "system": {
        "version": "v9.1",
        "shadow_dir": "/data/data/com.termux/files/home/OmegaCore/SHADOW_REALM"
    }
}

# ==========================================
# OMEGA PRIME: GENERATION 2 UPGRADE PACK
# Authorized by: User & Core
# ==========================================
config.update({
    'system_version': 2.0,
    'codename': 'ASCENSION',
    'status': 'ONLINE',
    'security_level': 'HIGH',
    'gen2_capabilities': [
        'autonomous_file_management',
        'dynamic_resilience',
        'shadow_realm_native'
    ]
})
