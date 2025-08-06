// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title YYS-SQR Trading Cards NFT
 * @dev ERC-721 NFT contract for YYS-SQR trading cards
 */
contract YYSSQRCards is ERC721, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Maps watermark ID to token ID
    mapping(string => uint256) public watermarkToToken;
    
    // Maps token ID to watermark ID
    mapping(uint256 => string) public tokenToWatermark;
    
    // Maps token ID to metadata URI
    mapping(uint256 => string) public tokenURIs;
    
    event CardMinted(
        address indexed to,
        uint256 indexed tokenId,
        string watermarkId,
        string metadataURI
    );
    
    constructor() ERC721("YYS-SQR Trading Cards", "YYSSQR") {}
    
    /**
     * @dev Mint NFT for a watermark ID
     */
    function mintCard(
        address to,
        string memory watermarkId,
        string memory metadataURI
    ) public onlyOwner returns (uint256) {
        require(watermarkToToken[watermarkId] == 0, "Card already minted");
        
        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();
        
        _safeMint(to, tokenId);
        
        watermarkToToken[watermarkId] = tokenId;
        tokenToWatermark[tokenId] = watermarkId;
        tokenURIs[tokenId] = metadataURI;
        
        emit CardMinted(to, tokenId, watermarkId, metadataURI);
        
        return tokenId;
    }
    
    /**
     * @dev Check if a watermark has been minted
     */
    function isCardMinted(string memory watermarkId) public view returns (bool) {
        return watermarkToToken[watermarkId] != 0;
    }
    
    /**
     * @dev Get token ID for watermark
     */
    function getTokenId(string memory watermarkId) public view returns (uint256) {
        return watermarkToToken[watermarkId];
    }
    
    /**
     * @dev Get watermark ID for token
     */
    function getWatermarkId(uint256 tokenId) public view returns (string memory) {
        return tokenToWatermark[tokenId];
    }
    
    /**
     * @dev Get token URI (metadata)
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "Token does not exist");
        return tokenURIs[tokenId];
    }
    
    /**
     * @dev Get total supply
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }
}