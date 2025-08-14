console.log('%c=== HAK-GAL GPU Monitor Quick Check ===', 'background: #222; color: #bada55; font-size: 14px; padding: 5px;');

// Check if store is available
if (window.__GOVERNOR_STORE__) {
    const store = window.__GOVERNOR_STORE__.getState();
    
    console.log('🔌 Connection Status:', store.isConnected ? '✅ CONNECTED' : '❌ DISCONNECTED');
    
    if (store.gpuInfo) {
        console.log('🎮 GPU Info:', {
            name: store.gpuInfo.name || 'Unknown',
            temperature: store.gpuInfo.temperature + '°C',
            utilization: store.gpuInfo.utilization + '%',
            memory: `${store.gpuInfo.memory_used} MB / ${store.gpuInfo.memory_total} MB`,
            power: store.gpuInfo.power_draw ? store.gpuInfo.power_draw + 'W' : 'N/A'
        });
    } else {
        console.log('⚠️ No GPU data yet. Waiting for updates...');
        console.log('💡 Tip: Check System Monitoring page or wait 3 seconds for next update');
    }
    
    // Subscribe to GPU updates
    const unsubscribe = window.__GOVERNOR_STORE__.subscribe((state) => {
        if (state.gpuInfo && state.gpuInfo.name) {
            console.log('🔄 GPU Update:', {
                temp: state.gpuInfo.temperature + '°C',
                usage: state.gpuInfo.utilization + '%',
                vram: Math.round(state.gpuInfo.memory_percent) + '% used'
            });
        }
    });
    
    console.log('📊 Subscribed to GPU updates. You should see updates every 3 seconds.');
    console.log('💡 To stop updates, run: unsubscribe()');
    
} else {
    console.log('❌ Store not available. Make sure you are on a HAK-GAL page.');
}
