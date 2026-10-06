const fs = require('fs');
const path = require('path');

const files = ['screen1.html', 'screen2.html', 'screen3.html', 'screen4.html', 'screen5.html', 'screen6.html'];
const componentNames = ['LiveDashboard', 'ScenarioBuilder', 'AARReports', 'UnitRoster', 'ReadinessMatrix', 'FlightRoster'];

files.forEach((file, index) => {
    let html = fs.readFileSync(path.join(__dirname, file), 'utf-8');
    
    // Extract everything inside <body>...</body>
    const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    if (!bodyMatch) return;
    
    let body = bodyMatch[1];
    
    // Remove the <script> tags
    body = body.replace(/<script[\s\S]*?<\/script>/gi, '');
    
    // Fix comments
    body = body.replace(/<!--([\s\S]*?)-->/g, '{/* $1 */}');
    
    // Convert class to className
    body = body.replace(/class=/g, 'className=');
    // Convert viewbox to viewBox
    body = body.replace(/viewbox=/g, 'viewBox=');
    // Convert for= to htmlFor=
    body = body.replace(/for=/g, 'htmlFor=');
    
    // Convert SVG attributes (dash case to camel case)
    const svgAttrs = ['preserveaspectratio', 'stroke-dasharray', 'stroke-width', 'stroke-opacity', 'fill-opacity', 'stroke-linecap', 'stroke-linejoin', 'clip-path', 'fill-rule', 'stop-color', 'stop-opacity'];
    const camelAttrs = ['preserveAspectRatio', 'strokeDasharray', 'strokeWidth', 'strokeOpacity', 'fillOpacity', 'strokeLinecap', 'strokeLinejoin', 'clipPath', 'fillRule', 'stopColor', 'stopOpacity'];
    
    svgAttrs.forEach((attr, i) => {
        const regex = new RegExp(attr + '=', 'g');
        body = body.replace(regex, camelAttrs[i] + '=');
    });

    // Fix <input> and <br> unclosed tags
    body = body.replace(/<input([^>]*?[^\/])>/g, '<input$1 />');
    body = body.replace(/<br([^>]*?[^\/])>/g, '<br$1 />');
    body = body.replace(/<img([^>]*?[^\/])>/g, '<img$1 />');
    body = body.replace(/<hr([^>]*?[^\/])>/g, '<hr$1 />');
    body = body.replace(/<animatetransform([^>]*?[^\/])>/g, '<animateTransform$1 />');
    body = body.replace(/<animate([^>]*?[^\/])>/g, '<animate$1 />');

    // Remove inline styles entirely for safety to prevent JSX parse errors (since Tailwind handles styling)
    body = body.replace(/style="[^"]*"/g, '');

    // Add empty hrefs for anchor tags without them
    body = body.replace(/<a([^>]*)>/g, (match) => match.includes('href') ? match : match.replace('<a', '<a href="#"'));

    // Create React component
    const componentCode = `import React from 'react';\n\nexport default function ${componentNames[index]}() {\n  return (\n    <div className="dark h-full overflow-y-auto">\n      ${body}\n    </div>\n  );\n}\n`;
    
    fs.writeFileSync(path.join(__dirname, `../frontend/src/${componentNames[index]}.tsx`), componentCode);
    console.log(`Converted ${file} to ${componentNames[index]}.tsx`);
});
