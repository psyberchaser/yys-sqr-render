// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProofOfScan v2
 * @dev This contract stores a record of a scan event, linking a unique ID
 * to the scanner's address, a timestamp, and now an IPFS content hash (CID).
 * This provides a more complete, on-chain reference for each scan.
 */
contract ProofOfScanV2 {

    struct Scan {
        address scanner;
        uint256 timestamp;
        string ipfsCid; // The IPFS hash of the watermarked file
    }

    // Maps the unique ID from the watermark to the latest scan details.
    mapping(string => Scan) public latestScan;

    event ScanRecorded(
        address indexed scanner,
        string uniqueId,
        string ipfsCid,
        uint256 timestamp
    );

    /**
     * @dev Records a scan event for a given unique ID and its associated IPFS CID.
     * The sender of the transaction is recorded as the scanner.
     * @param _uniqueId The unique identifier decoded from the watermark.
     * @param _ipfsCid The IPFS Content ID (hash) of the scanned file.
     */
    function recordScan(string memory _uniqueId, string memory _ipfsCid) public {
        latestScan[_uniqueId] = Scan({
            scanner: msg.sender,
            timestamp: block.timestamp,
            ipfsCid: _ipfsCid
        });
        emit ScanRecorded(msg.sender, _uniqueId, _ipfsCid, block.timestamp);
    }

    /**
     * @dev Retrieves the full details of the latest scan for a given unique ID.
     * @param _uniqueId The unique identifier to look up.
     * @return scanner The address of the account that performed the scan.
     * @return timestamp The block timestamp of when the scan was recorded.
     * @return ipfsCid The IPFS Content ID that was recorded with the scan.
     */
    function getScanDetails(string memory _uniqueId) public view returns (address scanner, uint256 timestamp, string memory ipfsCid) {
        Scan memory scanData = latestScan[_uniqueId];
        return (scanData.scanner, scanData.timestamp, scanData.ipfsCid);
    }
} 