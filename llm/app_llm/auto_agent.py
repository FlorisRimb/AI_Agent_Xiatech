import asyncio
from llama_cpp import Llama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json


class AutoInventoryAgent:
    """Autonomous LLM Agent for automatic inventory management."""
    
    def __init__(self, model_path: str):
        print(f"[AutoAgent] Loading model from {model_path}")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            verbose=False,
        )
        print("[AutoAgent] Model loaded successfully")
    
    async def autonomous_inventory_check(self) -> list:
        """Automatically check inventory and take actions."""
        print(f"\n[AutoAgent] Starting autonomous inventory check...")
        actions_taken = []
        
        server_params = StdioServerParameters(
            command="python",
            args=["mcp/server.py"],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Step 1: Check for products soon out of stock
                print("[AutoAgent] Checking for products at risk...")
                try:
                    risk_result = await session.call_tool("get_products_soon_out_of_stock", arguments={})
                    
                    if risk_result.content:
                        products_at_risk = []
                        for content in risk_result.content:
                            if hasattr(content, 'text'):
                                try:
                                    product_data = json.loads(content.text)
                                    products_at_risk.append(product_data)
                                except:
                                    pass
                        
                        print(f"[AutoAgent] Found {len(products_at_risk)} products at risk")
                        
                        # Step 2: For each product at risk, get stock levels and order
                        for product in products_at_risk:
                            sku = product.get('sku')
                            name = product.get('name')
                            
                            if not sku:
                                continue
                                
                            print(f"[AutoAgent] Processing {name} ({sku})")
                            
                            # Get current stock level
                            try:
                                stock_result = await session.call_tool("get_stock_levels_for_product", 
                                                                     arguments={"sku": sku})
                                
                                current_stock = 0
                                if stock_result.content and not stock_result.isError:
                                    try:
                                        for content in stock_result.content:
                                            if hasattr(content, 'text'):
                                                stock_data = json.loads(content.text)
                                                current_stock = stock_data.get('stock_on_hand', 0)
                                                break
                                    except:
                                        pass
                                
                                # Calculate order quantity intelligently
                                order_quantity = self._calculate_order_quantity(current_stock, sku)
                                
                                if order_quantity > 0:
                                    # Place the order
                                    print(f"[AutoAgent] Ordering {order_quantity} units of {name}")
                                    order_result = await session.call_tool("order_product", 
                                                                         arguments={
                                                                             "sku": sku, 
                                                                             "quantity": order_quantity
                                                                         })
                                    
                                    action = {
                                        "type": "stock_order",
                                        "product": name,
                                        "sku": sku,
                                        "current_stock": current_stock,
                                        "ordered_quantity": order_quantity,
                                        "reason": f"Stock critique ({current_stock} unités restantes)",
                                        "success": not order_result.isError
                                    }
                                    actions_taken.append(action)
                                    
                            except Exception as e:
                                print(f"[AutoAgent] Error processing {sku}: {e}")
                                action = {
                                    "type": "error",
                                    "product": name,
                                    "sku": sku,
                                    "reason": f"Erreur lors du traitement: {str(e)}",
                                    "success": False
                                }
                                actions_taken.append(action)
                    
                    else:
                        print("[AutoAgent] No products at risk found")
                        action = {
                            "type": "status_check",
                            "reason": "Aucun produit à risque détecté",
                            "success": True
                        }
                        actions_taken.append(action)
                        
                except Exception as e:
                    print(f"[AutoAgent] Error during inventory check: {e}")
                    action = {
                        "type": "error",
                        "reason": f"Erreur lors de la vérification: {str(e)}",
                        "success": False
                    }
                    actions_taken.append(action)
        
        return actions_taken
    
    def _calculate_order_quantity(self, current_stock: int, sku: str) -> int:
        """Calculate intelligent order quantity based on current stock."""
        # Base logic: order enough to reach 200 units (safety stock)
        target_stock = 200
        
        if current_stock < 20:
            # Critical: order to reach 300 units
            return max(300 - current_stock, 100)
        elif current_stock < 50:
            # Low: order to reach 200 units
            return max(target_stock - current_stock, 50)
        else:
            # Just top up to 150
            return max(150 - current_stock, 0)


async def run_autonomous_agent():
    """Run the autonomous agent once."""
    agent = AutoInventoryAgent("/app/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    actions = await agent.autonomous_inventory_check()
    
    print(f"\n[AutoAgent] Summary of actions taken:")
    for action in actions:
        print(f"  - {action}")
    
    return actions


if __name__ == "__main__":
    asyncio.run(run_autonomous_agent())
