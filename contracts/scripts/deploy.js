const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying YYS-SQR Cards NFT contract...");

  const YYSSQRCards = await ethers.getContractFactory("YYSSQRCards");
  const contract = await YYSSQRCards.deploy();

  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log("✅ YYSSQRCards deployed to:", contractAddress);
  console.log("🔗 Etherscan:", `https://sepolia.etherscan.io/address/${contractAddress}`);
  
  // Save deployment info
  const fs = require('fs');
  const deploymentInfo = {
    contractAddress: contractAddress,
    deploymentTime: new Date().toISOString(),
    network: "sepolia",
    contractName: "YYSSQRCards"
  };
  
  fs.writeFileSync('deployment.json', JSON.stringify(deploymentInfo, null, 2));
  console.log("📄 Deployment info saved to deployment.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });