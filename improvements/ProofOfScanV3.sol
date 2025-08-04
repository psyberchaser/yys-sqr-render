// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ProofOfScan v3 - Enhanced Watermark Verification System
 * @dev Advanced contract with multiple scan history, metadata, and access control
 */
contract ProofOfScanV3 is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _scanCounter;
    
    struct Scan {
        address scanner;
        uint256 timestamp;
        string ipfsCid;
        string metadata; // Additional metadata (location, device, etc.)
        uint256 scanNumber; // Sequential scan number for this ID
    }
    
    struct WatermarkInfo {
        address creator;
        uint256 createdAt;
        string originalIpfsCid;
        bool isActive;
        uint256 totalScans;
        uint256 maxScans; // 0 = unlimited, >0 = limited scans
    }
    
    // Maps unique ID to watermark info
    mapping(string => WatermarkInfo) public watermarks;
    
    // Maps unique ID to array of all scans
    mapping(string => Scan[]) public scanHistory;
    
    // Maps unique ID to latest scan (for backward compatibility)
    mapping(string => Scan) public latestScan;
    
    // Maps scanner address to their scan count
    mapping(address => uint256) public scannerStats;
    
    event WatermarkRegistered(
        string indexed uniqueId,
        address indexed creator,
        string originalIpfsCid,
        uint256 maxScans,
        uint256 timestamp
    );
    
    event ScanRecorded(
        address indexed scanner,
        string indexed uniqueId,
        string ipfsCid,
        uint256 scanNumber,
        uint256 timestamp
    );
    
    event WatermarkDeactivated(
        string indexed uniqueId,
        address indexed deactivatedBy,
        uint256 timestamp
    );
    
    /**
     * @dev Register a new watermark (called when embedding)
     */
    function registerWatermark(
        string memory _uniqueId,
        string memory _originalIpfsCid,
        uint256 _maxScans
    ) public {
        require(bytes(_uniqueId).length > 0, "Invalid unique ID");
        require(watermarks[_uniqueId].creator == address(0), "Watermark already exists");
        
        watermarks[_uniqueId] = WatermarkInfo({
            creator: msg.sender,
            createdAt: block.timestamp,
            originalIpfsCid: _originalIpfsCid,
            isActive: true,
            totalScans: 0,
            maxScans: _maxScans
        });
        
        emit WatermarkRegistered(_uniqueId, msg.sender, _originalIpfsCid, _maxScans, block.timestamp);
    }
    
    /**
     * @dev Record a scan event with enhanced features
     */
    function recordScan(
        string memory _uniqueId,
        string memory _ipfsCid,
        string memory _metadata
    ) public nonReentrant {
        require(bytes(_uniqueId).length > 0, "Invalid unique ID");
        require(watermarks[_uniqueId].isActive, "Watermark is not active");
        
        WatermarkInfo storage watermark = watermarks[_uniqueId];
        
        // Check scan limits
        if (watermark.maxScans > 0) {
            require(watermark.totalScans < watermark.maxScans, "Scan limit exceeded");
        }
        
        _scanCounter.increment();
        uint256 scanNumber = watermark.totalScans + 1;
        
        Scan memory newScan = Scan({
            scanner: msg.sender,
            timestamp: block.timestamp,
            ipfsCid: _ipfsCid,
            metadata: _metadata,
            scanNumber: scanNumber
        });
        
        // Update mappings
        scanHistory[_uniqueId].push(newScan);
        latestScan[_uniqueId] = newScan;
        watermark.totalScans++;
        scannerStats[msg.sender]++;
        
        // Auto-deactivate if max scans reached
        if (watermark.maxScans > 0 && watermark.totalScans >= watermark.maxScans) {
            watermark.isActive = false;
            emit WatermarkDeactivated(_uniqueId, msg.sender, block.timestamp);
        }
        
        emit ScanRecorded(msg.sender, _uniqueId, _ipfsCid, scanNumber, block.timestamp);
    }
    
    /**
     * @dev Get complete watermark information
     */
    function getWatermarkInfo(string memory _uniqueId) 
        public view returns (
            address creator,
            uint256 createdAt,
            string memory originalIpfsCid,
            bool isActive,
            uint256 totalScans,
            uint256 maxScans
        ) 
    {
        WatermarkInfo memory info = watermarks[_uniqueId];
        return (
            info.creator,
            info.createdAt,
            info.originalIpfsCid,
            info.isActive,
            info.totalScans,
            info.maxScans
        );
    }
    
    /**
     * @dev Get scan history for a watermark
     */
    function getScanHistory(string memory _uniqueId) 
        public view returns (Scan[] memory) 
    {
        return scanHistory[_uniqueId];
    }
    
    /**
     * @dev Get scan count for a specific scanner
     */
    function getScannerStats(address _scanner) 
        public view returns (uint256) 
    {
        return scannerStats[_scanner];
    }
    
    /**
     * @dev Deactivate a watermark (only creator or owner)
     */
    function deactivateWatermark(string memory _uniqueId) public {
        require(
            watermarks[_uniqueId].creator == msg.sender || owner() == msg.sender,
            "Not authorized"
        );
        require(watermarks[_uniqueId].isActive, "Already inactive");
        
        watermarks[_uniqueId].isActive = false;
        emit WatermarkDeactivated(_uniqueId, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get total number of scans across all watermarks
     */
    function getTotalScans() public view returns (uint256) {
        return _scanCounter.current();
    }
    
    /**
     * @dev Emergency function to pause contract (owner only)
     */
    function emergencyPause() public onlyOwner {
        // Implementation for emergency pause
    }
}