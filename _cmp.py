import json

# 原始快照结构
data = json.load(open('snapshot.json', encoding='utf-8'))

def show_tree(n, indent=0):
    prefix = '  ' * indent
    nc = n['node_class']
    dt = n.get('data_type', '')
    extra = f' [{dt}]' if nc == 'Variable' else ''
    print(f'{prefix}{n["browse_name"]}  {nc}{extra}')
    for c in n.get('children', []):
        show_tree(c, indent + 1)

print('=== 原始服务器结构 ===')
sov1 = data['nodes'][0]['children'][0]
show_tree(sov1)
